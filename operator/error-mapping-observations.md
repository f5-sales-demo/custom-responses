# Error-mapping observations

Retained investigation details from the reader guide during issue #58. The dated acceptance record remains authoritative; this editorial work does not requalify traffic.

## Observed mapping limits

The checks below were repeated with trusted TLS over HTTP/1.1 and HTTP/2 on 2026-10-06. Direct fixture responses and private origin logs confirmed the origin-backed results.

| Test | Observed response | Custom mapping status |
| --- | --- | --- |
| `/status/302`, `/status/418`, `/status/500` | Original status and origin body retained | Class `3`, `4`, and `5` replacement of these origin bodies is **un-verified**. |
| `/status/404`, `/status/503` | Original status and origin body retained | Exact `404` and `503` replacement of these origin bodies is **un-verified**. |
| `/fault/500` | Origin `500` and origin body retained | Class `5` replacement of this origin body is **un-verified**. |
| `/fault/502` | Edge `503` with “Exact 503” after an upstream reset | The path name does not establish a `502`; a custom `502` example is **un-verified**. |
| Oversized request header | Edge `431` with a generic body | Class `4` did not apply to this request-parser response. |
| Malformed request method | Edge `400` with a generic body | Class `4` did not apply to this request-parser response. |

The accepted API configuration contained all five mappings and matched the source. The API field description defines class keys and exact-code precedence, but it does not establish
that every response path is eligible. Use the two verified upstream-fault examples above when demonstrating mapped pages. Keep the remaining mappings as **un-verified**
configuration examples; do not treat a passing origin-status control as proof that its body was replaced.
