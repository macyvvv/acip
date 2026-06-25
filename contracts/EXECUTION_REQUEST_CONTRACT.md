# EXECUTION_REQUEST_CONTRACT

request_id: string
request_status: pending_approval | ready | completed | failed
request_priority: integer
approval_required: boolean
dependency: list[string]
worker_assignment: string | null
