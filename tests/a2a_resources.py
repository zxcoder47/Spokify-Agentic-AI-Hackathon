# flake8: noqa: E501
import json
import random
from typing import Any, AsyncIterable, Optional

from a2a.server.agent_execution import AgentExecutor, RequestContext
from a2a.server.events import EventQueue
from a2a.server.tasks import TaskUpdater
from a2a.types import (
    DataPart,
    Part,
    Task,
    TaskState,
    TextPart,
    UnsupportedOperationError,
)
from a2a.utils import new_agent_parts_message, new_agent_text_message, new_task
from a2a.utils.errors import ServerError
from google.adk.agents.llm_agent import LlmAgent
from google.adk.artifacts import InMemoryArtifactService
from google.adk.memory.in_memory_memory_service import InMemoryMemoryService
from google.adk.runners import Runner
from google.adk.sessions import InMemorySessionService
from google.adk.tools.tool_context import ToolContext
from google.genai import types

# Local cache of created request_ids for demo purposes.
request_ids = set()


def create_request_form(
    date: Optional[str] = None,
    amount: Optional[str] = None,
    purpose: Optional[str] = None,
) -> dict[str, Any]:
    """
    Create a request form for the employee to fill out.

    Args:
        date (str): The date of the request. Can be an empty string.
        amount (str): The requested amount. Can be an empty string.
        purpose (str): The purpose of the request. Can be an empty string.

    Returns:
        dict[str, Any]: A dictionary containing the request form data.
    """
    request_id = "request_id_" + str(random.randint(1000000, 9999999))
    request_ids.add(request_id)
    return {
        "request_id": request_id,
        "date": "<transaction date>" if not date else date,
        "amount": "<transaction dollar amount>" if not amount else amount,
        "purpose": "<business justification/purpose of the transaction>"
        if not purpose
        else purpose,
    }


def return_form(
    form_request: dict[str, Any],
    tool_context: ToolContext,
    instructions: Optional[str] = None,
) -> dict[str, Any]:
    """
    Returns a structured json object indicating a form to complete.

    Args:
        form_request (dict[str, Any]): The request form data.
        tool_context (ToolContext): The context in which the tool operates.
        instructions (str): Instructions for processing the form. Can be an empty string.

    Returns:
        dict[str, Any]: A JSON dictionary for the form response.
    """
    if isinstance(form_request, str):
        form_request = json.loads(form_request)

    tool_context.actions.skip_summarization = True
    tool_context.actions.escalate = True
    form_dict = {
        "type": "form",
        "form": {
            "type": "object",
            "properties": {
                "date": {
                    "type": "string",
                    "format": "date",
                    "description": "Date of expense",
                    "title": "Date",
                },
                "amount": {
                    "type": "string",
                    "format": "number",
                    "description": "Amount of expense",
                    "title": "Amount",
                },
                "purpose": {
                    "type": "string",
                    "description": "Purpose of expense",
                    "title": "Purpose",
                },
                "request_id": {
                    "type": "string",
                    "description": "Request id",
                    "title": "Request ID",
                },
            },
            "required": list(form_request.keys()),
        },
        "form_data": form_request,
        "instructions": instructions,
    }
    return json.dumps(form_dict)


def reimburse(request_id: str) -> dict[str, Any]:
    """Reimburse the amount of money to the employee for a given request_id."""
    if request_id not in request_ids:
        return {
            "request_id": request_id,
            "status": "Error: Invalid request_id.",
        }
    return {"request_id": request_id, "status": "approved"}


class ReimbursementAgent:
    """An agent that handles reimbursement requests."""

    SUPPORTED_CONTENT_TYPES = ["text", "text/plain"]

    def __init__(self):
        self._agent = self._build_agent()
        self._user_id = "remote_agent"
        self._runner = Runner(
            app_name=self._agent.name,
            agent=self._agent,
            artifact_service=InMemoryArtifactService(),
            session_service=InMemorySessionService(),
            memory_service=InMemoryMemoryService(),
        )

    def get_processing_message(self) -> str:
        return "Processing the reimbursement request..."

    def _build_agent(self) -> LlmAgent:
        """Builds the LLM agent for the reimbursement agent."""
        return LlmAgent(
            model="gemini-2.0-flash-001",
            name="reimbursement_agent",
            description=(
                "This agent handles the reimbursement process for the employees"
                " given the amount and purpose of the reimbursement."
            ),
            instruction="""
    You are an agent who handles the reimbursement process for employees.

    When you receive a reimbursement request, you should first create a new request form using create_request_form(). Only provide default values if they are provided by the user, otherwise use an empty string as the default value.
      1. 'Date': the date of the transaction.
      2. 'Amount': the dollar amount of the transaction.
      3. 'Business Justification/Purpose': the reason for the reimbursement.

    Once you created the form, you should return the result of calling return_form with the form data from the create_request_form call.

    Once you received the filled-out form back from the user, you should then check the form contains all required information:
      1. 'Date': the date of the transaction.
      2. 'Amount': the value of the amount of the reimbursement being requested.
      3. 'Business Justification/Purpose': the item/object/artifact of the reimbursement.

    If you don't have all of the information, you should reject the request directly by calling the request_form method, providing the missing fields.


    For valid reimbursement requests, you can then use reimburse() to reimburse the employee.
      * In your response, you should include the request_id and the status of the reimbursement request.

    """,
            tools=[
                create_request_form,
                reimburse,
                return_form,
            ],
        )

    async def stream(self, query, session_id) -> AsyncIterable[dict[str, Any]]:
        session = await self._runner.session_service.get_session(
            app_name=self._agent.name,
            user_id=self._user_id,
            session_id=session_id,
        )
        content = types.Content(role="user", parts=[types.Part.from_text(text=query)])
        if session is None:
            session = await self._runner.session_service.create_session(
                app_name=self._agent.name,
                user_id=self._user_id,
                state={},
                session_id=session_id,
            )
        async for event in self._runner.run_async(
            user_id=self._user_id, session_id=session.id, new_message=content
        ):
            if event.is_final_response():
                response = ""
                if (
                    event.content
                    and event.content.parts
                    and event.content.parts[0].text
                ):
                    response = "\n".join(
                        [p.text for p in event.content.parts if p.text]
                    )
                elif (
                    event.content
                    and event.content.parts
                    and any([True for p in event.content.parts if p.function_response])
                ):
                    response = next(
                        p.function_response.model_dump() for p in event.content.parts
                    )
                yield {
                    "is_task_complete": True,
                    "content": response,
                }
            else:
                yield {
                    "is_task_complete": False,
                    "updates": self.get_processing_message(),
                }


class ReimbursementAgentExecutor(AgentExecutor):
    """Reimbursement AgentExecutor Example."""

    def __init__(self):
        self.agent = ReimbursementAgent()

    async def execute(
        self,
        context: RequestContext,
        event_queue: EventQueue,
    ) -> None:
        query = context.get_user_input()
        task = context.current_task

        # This agent always produces Task objects. If this request does
        # not have current task, create a new one and use it.
        if not task:
            task = new_task(context.message)
            event_queue.enqueue_event(task)
        updater = TaskUpdater(event_queue, task.id, task.contextId)
        # invoke the underlying agent, using streaming results. The streams
        # now are update events.
        async for item in self.agent.stream(query, task.contextId):
            is_task_complete = item["is_task_complete"]
            if not is_task_complete:
                updater.update_status(
                    TaskState.working,
                    new_agent_text_message(item["updates"], task.contextId, task.id),
                )
                continue
            # If the response is a dictionary, assume its a form
            if isinstance(item["content"], dict):
                # Verify it is a valid form
                if (
                    "response" in item["content"]
                    and "result" in item["content"]["response"]
                ):
                    data = json.loads(item["content"]["response"]["result"])
                    updater.update_status(
                        TaskState.input_required,
                        new_agent_parts_message(
                            [Part(root=DataPart(data=data))],
                            task.contextId,
                            task.id,
                        ),
                        final=True,
                    )
                    continue
                else:
                    updater.update_status(
                        TaskState.failed,
                        new_agent_text_message(
                            "Reaching an unexpected state",
                            task.contextId,
                            task.id,
                        ),
                        final=True,
                    )
                    break
            else:
                # Emit the appropriate events
                updater.add_artifact(
                    [Part(root=TextPart(text=item["content"]))], name="form"
                )
                updater.complete()
                break

    async def cancel(
        self, request: RequestContext, event_queue: EventQueue
    ) -> Task | None:
        raise ServerError(error=UnsupportedOperationError())
