# Repository Knowledge Graph Schema

## Node Schema

| Field | Required | Description |
|---|---:|---|
| id | yes | stable node id |
| type | yes | policy / adr / wbs / runbook / contract / workflow / script / registry / catalog / asset / readme |
| path | yes | repository path |
| title | no | H1 or derived title |
| status | no | lifecycle status |
| source | yes | repository |

## Edge Schema

| Field | Required | Description |
|---|---:|---|
| source | yes | source node id |
| target | yes | target node id |
| type | yes | references / validates / governs / implements / depends_on |
| evidence | no | file line or source text |
