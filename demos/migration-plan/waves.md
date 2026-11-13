# Migration waves (generated)

> Independent portfolio demo. Synthetic inventory.

## Wave 0 - shared services

| Server | OS | Role | Criticality | Target size |
|---|---|---|---|---|
| DEMO-DC01 | Windows Server 2019 | Domain controller | high | Standard_B2ms |

## Wave 1 - LabPortal

| Server | OS | Role | Criticality | Target size |
|---|---|---|---|---|
| DEMO-DEV01 | Windows Server 2019 | Dev/test | low | Standard_B2ms |

## Wave 2 - Ops

| Server | OS | Role | Criticality | Target size |
|---|---|---|---|---|
| DEMO-LNX05 | RHEL 7 | Monitoring agent host | low | Standard_B2s |

## Wave 3 - Reports, SampleTracker

| Server | OS | Role | Criticality | Target size |
|---|---|---|---|---|
| DEMO-LNX01 | RHEL 8 | Nginx reverse proxy | medium | Standard_B2s |
| DEMO-LNX02 | RHEL 8 | Java app (Tomcat) | medium | Standard_D4s_v5 |
| DEMO-LNX03 | Ubuntu 20.04 | PostgreSQL 13 | medium | Standard_E2s_v5 |
| DEMO-LNX04 | Ubuntu 22.04 | Batch jobs | low | Standard_B2ms |

## Wave 4 - LabPortal, Shared

| Server | OS | Role | Criticality | Target size |
|---|---|---|---|---|
| DEMO-APP01 | Windows Server 2019 | App server | high | Standard_D4s_v5 |
| DEMO-FS01 | Windows Server 2012 R2 | File server | medium | Standard_D2s_v5 |
| DEMO-SQL01 | Windows Server 2019 | SQL Server 2019 | high | Standard_E4s_v5 |
| DEMO-WEB01 | Windows Server 2016 | IIS web | high | Standard_D2s_v5 |
| DEMO-WEB02 | Windows Server 2016 | IIS web | high | Standard_D2s_v5 |

