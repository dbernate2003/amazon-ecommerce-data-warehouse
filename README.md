# Amazon E-Commerce Data Warehouse

End-to-end data warehouse project built on a real 10 GB Amazon
e-commerce dataset. The goal was to design and implement a complete
analytical pipeline — from raw data ingestion to business intelligence
dashboards — applying the practices used in professional data teams.

---

## What this project covers

This project goes through every stage of a real data warehouse:
exploring and profiling the source data, estimating storage
requirements through volumetry analysis, designing the dimensional
model following Kimball methodology, building a three-layer Medallion
architecture, documenting the ETL pipeline with full column lineage,
and delivering a BI dashboard on top of the Gold layer.

---

## Tech stack

| Tool                   | Purpose                                       |
|------------------------|-----------------------------------------------|
| SQL (MySQL/PostgreSQL) | Source data exploration and dimensional model |
| Python / pandas        | ETL transformations and data profiling        |
| Power BI / Tableau     | Dashboard and business intelligence layer     |
| Git / GitHub           | Version control and team collaboration        |
| Notion                 | Project documentation and knowledge base      |

---

## Architecture

The pipeline follows the Medallion architecture, where each layer
has a single responsibility and the previous layer is never modified.

Source — Amazon e-commerce database (~10 GB)
        |
     BRONZE
     Raw data loaded exactly as it comes from the source.
     Nothing is modified here. If something breaks
     downstream, we reprocess from this layer.
        |
     SILVER
     Data is cleaned, standardized, and integrated.
     Surrogate keys are generated. Nulls and
     inconsistencies are resolved and documented.
        |
      GOLD
     Star schema ready for analysis.
     This is the only layer exposed to dashboards
     and end users.
        |
   Dashboard
   Built on the Gold layer.

---

## Dimensional model

The design follows Kimball's four-step methodology:

1. Identify the business process — e-commerce sales transactions
2. Define the grain — one row equals one product within one order
3. Identify the dimensions — Product, Customer, Date, Location, Seller
4. Identify the facts — quantity sold, revenue, discount applied

Every dimension table uses a surrogate key as its primary key and
keeps the original source key as a separate attribute for
traceability. Each dimension includes a row with surrogate key -1
labeled Unknown, to handle facts that arrive without a matching
dimension record and avoid null foreign keys in the fact table.

Every metric in the fact table is classified:

- Additive: quantity, revenue — can be summed across all dimensions
- Semi-additive: inventory levels — can be summed across locations
  but not across time periods
- Non-additive: discount rate, unit price — stored as their additive
  components and recalculated at query or dashboard time

---

## Repository structure

    amazon-ecommerce-data-warehouse/
    |
    |-- bronze/     Source exploration scripts and raw data load
    |-- silver/     Cleaning and transformation scripts
    |-- gold/       Star schema DDL and dimensional model
    |-- etl/        ETL pipeline scripts and lineage documentation
    |-- docs/       Volumetry analysis, requirements, data dictionary
    |-- dashboard/  Dashboard screenshots and report exports

---

## Branch strategy

| Branch                     | Purpose                                    |
|----------------------------|--------------------------------------------|
| main                       | Production — merge only after team review  |
| dev                        | Integration branch before merging to main  |
| feature/bronze-exploration | Source profiling and raw data load         |
| feature/silver-cleaning    | Cleaning rules and surrogate key generation|
| feature/gold-star-schema   | Dimensional model implementation           |
| feature/etl-pipeline       | Full ETL pipeline and lineage documentation|
| feature/bi-dashboard       | Dashboard development and exports          |
| docs/project-documentation | Written deliverables and analysis          |

---

## Project status

| Phase                          | Status      |
|--------------------------------|-------------|
| Source exploration and volumetry | In progress |
| Conceptual model               | Pending     |
| Logical model — star schema    | Pending     |
| ETL pipeline and Medallion     | Pending     |
| Requirements documentation     | Pending     |
| BI dashboard                   | Pending     |

---

## Volumetry summary

Estimated storage per layer based on source dataset profiling.
Full calculation with formulas, assumptions, and growth projections
is documented in docs/volumetry.md.

| Layer  | Current rows | Bytes per row | Current size | Size at 5 years |
|--------|--------------|---------------|--------------|-----------------|
| Bronze | TBD          | TBD           | ~10 GB       | TBD             |
| Silver | TBD          | TBD           | TBD          | TBD             |
| Gold   | TBD          | TBD           | TBD          | TBD             |

---

## Key design decisions

**Why star schema over snowflake.** The star schema minimizes the
number of joins at query time, which directly impacts dashboard
performance. A snowflake design would only be justified if a
dimension grew large enough that redundancy became a measurable
storage problem — which the volumetry analysis does not support here.

**Why surrogate keys.** The source dataset may contain overlapping
identifiers across systems. Surrogate keys decouple the warehouse
from the source, making the model stable even if source keys change.

**Why Bronze is never modified.** Treating the raw layer as
append-only means any transformation error in Silver or Gold can
be fully reprocessed from the original data without returning to
the source system.

---

## Author

Dario — Systems Engineering Student, Universidad Popular del Cesar
Colombia — Aspiring Data Engineer

Academic project — Bases de Datos Avanzadas course
