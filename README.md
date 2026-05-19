# BI Analytics Platform

Plataforma completa de Business Intelligence e Analytics com frontend React, backend FastAPI, pipeline ETL, e Metabase integrado — tudo orquestrado com Docker.

## Arquitetura

```mermaid
flowchart TB
    subgraph Frontend["Frontend (React + Vite)"]
        A1["Dashboard (/)"]
        A2["Vendas (/vendas)"]
        A3["Clientes (/clientes)"]
        A4["Produtos (/produtos)"]
        A5["Tendências (/tendencias)"]
        A6["Configurações (/configuracoes)"]
    end

    subgraph Backend["Backend (FastAPI + Python)"]
        B1["API REST<br/>(porta 8000)"]
        B2["WebSocket<br/>(/ws)"]
        B3["Cache Layer<br/>(Redis)"]
        B4["Serviços Analytics<br/>(Pandas/NumPy)"]
        B5["Exportação<br/>(CSV/PDF)"]
    end

    subgraph Database["Banco de Dados"]
        C1[(PostgreSQL<br/>bi_platform)]
        C2[(Redis<br/>Cache)]
    end

    subgraph ETL["Pipeline ETL"]
        D1["Import<br/>(CSV / APIs)"]
        D2["Transform<br/>(Limpeza / Agregação)"]
        D3["Load<br/>(Upsert / Incremental)"]
    end

    subgraph Metabase["Metabase BI (porta 3001)"]
        E1["Dashboards"]
        E2["Alertas"]
        E3["SQL Ad-hoc"]
    end

    Frontend <-->|HTTP / REST| Backend
    Backend -->|Atualizações tempo real| Frontend
    Backend <--> B3
    B3 <--> C2
    B4 <--> C1
    D1 --> D2 --> D3 --> C1
    ETL -->|Alimenta| C1
    Metabase -->|Consultas SQL| C1
    Backend -->|ETL agendado| ETL
```

## Fluxo de Dados

```mermaid
sequenceDiagram
    participant User as Usuário
    participant FE as Frontend (React)
    participant API as API (FastAPI)
    participant Cache as Redis Cache
    participant DB as PostgreSQL
    participant ETL as Pipeline ETL

    Note over ETL: Agendado via cron (2:00 AM)
    ETL->>ETL: Extract (CSV / API externa)
    ETL->>ETL: Transform (limpeza, normalização)
    ETL->>ETL: Load (upsert)
    ETL->>DB: Dados processados

    User->>FE: Acessa dashboard
    FE->>API: GET /analytics/dashboard
    API->>Cache: Verifica cache
    alt Cache hit
        Cache-->>API: Dados cacheados
    else Cache miss
        API->>DB: Query SQL (agregações)
        DB-->>API: Resultados
        API->>Cache: Armazena em cache (TTL 300s)
    end
    API-->>FE: JSON com KPIs
    FE->>FE: Renderiza gráficos (Recharts)

    User->>FE: Filtra por período
    FE->>API: GET /analytics/sales?period=month
    API-->>FE: Dados filtrados
```

## Tecnologias

```mermaid
mindmap
  BI Analytics Platform
    Frontend
      React 18 + TypeScript
      Vite 5
      TailwindCSS 3
      Recharts (gráficos)
      TanStack Table
      date-fns
      Lucide React
    Backend
      Python 3.11
      FastAPI
      SQLAlchemy 2.0
      Pandas / NumPy
      Redis (cache)
      WebSockets
      ReportLab (PDF)
    Infraestrutura
      Docker / Compose
      PostgreSQL 15
      Redis 7
      Metabase
      GitHub Actions
```

## Funcionalidades

| Funcionalidade | Descrição |
|---|---|
| **Dashboard** | 5 KPIs (Receita, Pedidos, Clientes Ativos, Ticket Médio, Conversão) com indicador de crescimento |
| **Relatório de Vendas** | Vendas por dia, categoria, método de pagamento, top produtos |
| **Relatório de Clientes** | Distribuição por tier, região, top clientes, taxa de retenção |
| **Relatório de Produtos** | Top vendidos, estoque baixo, distribuição por categoria |
| **Análise de Tendências** | Sazonalidade, previsão de receita, crescimento de clientes |
| **Exportação** | CSV e PDF de qualquer relatório |
| **Filtro por Período** | Hoje, 7 dias, mês, ano ou personalizado |
| **Modo Escuro** | Alterna entre claro/escuro |
| **SQL Customizado** | Consulta SQL livre na página de configurações |
| **WebSocket** | Atualizações em tempo real |
| **Metabase** | BI avançado com dashboards, alertas e análises ad-hoc |
| **ETL Automatizado** | Pipeline agendado via GitHub Actions |

## Quick Start

### Pré-requisitos

- Docker e Docker Compose
- Node.js 20+ (desenvolvimento local do frontend)
- Python 3.11+ (desenvolvimento local do backend)

### Executando com Docker

```bash
docker compose up -d
```

Isso inicia todos os serviços: PostgreSQL, Redis, Backend, Frontend e Metabase.

**Acessar:**
| Serviço | URL |
|---|---|
| Frontend | http://localhost:5173 |
| Backend API | http://localhost:8000/docs |
| Metabase | http://localhost:3001 |

### Populando o Banco com Dados de Exemplo

Após iniciar os containers, execute o seed para gerar 90 dias de dados fictícios:

```bash
docker exec bi-backend python seed.py
```

> O seed cria 12 produtos, 12 clientes e ~700 vendas com pagamentos, descontos e status variados.

## Estrutura do Projeto

```mermaid
flowchart LR
    subgraph root["bi-platform/"]
        direction TB
        FE["frontend/"] --> FE_SRC["src/"]
        FE_SRC --> PAGES["pages/<br/>Dashboard, Vendas,<br/>Clientes, Produtos,<br/>Tendências, Config"]
        FE_SRC --> COMP["components/<br/>Layout, KPICard,<br/>DataTable, Charts"]
        FE_SRC --> HOOKS["hooks/<br/>useApi, useWebSocket"]
        FE_SRC --> SERVICES["services/api.ts"]
        FE_SRC --> TYPES["types/"]

        BE["backend/"] --> BE_APP["app/"]
        BE_APP --> ROUTES["routes/<br/>analytics, export"]
        BE_APP --> SERVICES_BE["services/<br/>analytics_service"]
        BE_APP --> MODELS["models.py"]
        BE_APP --> SCHEMAS["schemas.py"]
        BE_APP --> DATABASE["database.py"]
        BE_APP --> CACHE["cache.py"]

        ETL["etl/"] --> ETL_JOBS["jobs/<br/>import_daily_sales,<br/>aggregate_metrics,<br/>cleanup_old_data"]
        ETL --> EXTRACT["extract.py"]
        ETL --> TRANSFORM["transform.py"]
        ETL --> LOAD["load.py"]

        META["metabase/"] --> META_SQL["init.sql"]
        META --> META_DOCKER["Dockerfile"]

        ROOT_FILES["docker-compose.yml<br/>.env<br/>.github/workflows/"]
    end
```

```
bi-platform/
├── frontend/                  # React + Vite + TypeScript
│   ├── src/
│   │   ├── pages/             # Dashboard, Vendas, Clientes, Produtos, Tendências, Config
│   │   ├── components/        # Layout, KPICard, DataTable, Charts (Line, Bar, Pie)
│   │   ├── hooks/             # useApi, useWebSocket, useDarkMode
│   │   ├── services/          # api.ts (axios, timeout 30s)
│   │   ├── types/             # Interfaces TypeScript
│   │   └── utils/             # date.ts, format.ts (locale pt-BR)
│   ├── Dockerfile
│   └── package.json
│
├── backend/                   # Python FastAPI
│   ├── app/
│   │   ├── routes/            # analytics.py, export.py
│   │   ├── services/          # analytics_service.py (consultas SQL + Pandas)
│   │   ├── models.py          # Product, Customer, Sale, SaleItem, ETLJobLog
│   │   ├── schemas.py         # Pydantic (DashboardKPI, SalesReport, ...)
│   │   ├── database.py        # SQLAlchemy engine, init_db()
│   │   ├── cache.py           # Redis cache (async)
│   │   ├── config.py          # Config (variáveis de ambiente)
│   │   └── main.py            # FastAPI app com lifespan
│   ├── seed.py                # Dados de exemplo
│   ├── tests/
│   ├── requirements.txt
│   └── Dockerfile
│
├── etl/                       # Pipeline ETL standalone
│   ├── jobs/
│   │   ├── import_daily_sales.py   # Importa CSV (ou gera dados de exemplo)
│   │   ├── aggregate_metrics.py     # Agrega métricas diárias
│   │   └── cleanup_old_data.py      # Limpa dados antigos
│   ├── extract.py             # Extractor (CSV, JSON, Excel, API REST)
│   ├── transform.py           # Transformer (limpeza, normalização)
│   ├── load.py                # Loader (upsert, incremental)
│   ├── runner.py              # CLI: once | schedule | import | aggregate | cleanup
│   ├── database.py
│   └── config.py
│
├── metabase/                  # Configuração Metabase
│   ├── Dockerfile
│   └── init.sql
│
├── .github/workflows/         # GitHub Actions (CI/CD + ETL agendado)
└── docker-compose.yml         # Orquestração
```

## Modelo de Dados

```mermaid
erDiagram
    CUSTOMERS ||--o{ SALES : "1:N"
    PRODUCTS ||--o{ SALE_ITEMS : "1:N"
    SALES ||--o{ SALE_ITEMS : "1:N"

    CUSTOMERS {
        int id PK
        string name
        string email UK
        string phone
        string city
        string state
        string country
        enum tier "bronze|silver|gold|platinum"
        int total_purchases
        float total_spent
        datetime first_purchase_date
        datetime last_purchase_date
        boolean is_active
        datetime created_at
    }

    PRODUCTS {
        int id PK
        string name
        string sku UK
        string category
        text description
        float unit_price
        float cost_price
        int stock_quantity
        datetime created_at
        datetime updated_at
    }

    SALES {
        int id PK
        string invoice_number UK
        int customer_id FK
        datetime sale_date
        float total_amount
        float discount
        float tax
        float final_amount
        string payment_method
        enum status "completed|cancelled|refunded|pending"
        datetime created_at
    }

    SALE_ITEMS {
        int id PK
        int sale_id FK
        int product_id FK
        int quantity
        float unit_price
        float total_price
    }

    ETL_JOB_LOGS {
        int id PK
        string job_name
        string status
        datetime started_at
        datetime finished_at
        int rows_processed
        text error_message
        datetime created_at
    }
```

## Endpoints da API

### Analytics

| Método | Rota | Descrição | Parâmetros |
|---|---|---|---|
| GET | `/analytics/dashboard` | KPIs (receita, pedidos, ticket médio, conversão) | `start_date`, `end_date` |
| GET | `/analytics/sales` | Relatório completo de vendas | `start_date`, `end_date`, `period` |
| GET | `/analytics/customers` | Relatório de clientes | `start_date`, `end_date` |
| GET | `/analytics/products` | Relatório de produtos | `start_date`, `end_date` |
| GET | `/analytics/trends` | Tendências e sazonalidade | `months` (3-36) |
| POST | `/analytics/custom-query` | SQL personalizado | `query`, `params` |
| POST | `/analytics/cache/invalidate` | Limpa cache | `pattern` |

### Exportação

| Método | Rota | Descrição |
|---|---|---|
| GET | `/export/csv` | Exportar CSV |
| GET | `/export/pdf` | Exportar PDF |

### WebSocket

| Rota | Descrição |
|---|---|
| `/ws` | Atualizações em tempo real (cache invalidado) |

## Desenvolvimento Local

### Backend

```bash
cd backend
python -m venv venv
# Windows:
.\venv\Scripts\activate
# Linux/Mac:
# source venv/bin/activate
pip install -r requirements.txt
uvicorn app.main:app --reload
```

### Frontend

```bash
cd frontend
npm install
npm run dev
```

### ETL Pipeline

```bash
cd etl
pip install -r requirements.txt
python runner.py once       # Executa todos os jobs uma vez
python runner.py import     # Só o job de importação
python runner.py aggregate  # Só agregação
python runner.py schedule   # Modo agendado (cron)
```

## Metabase

### Setup Inicial

1. Acesse http://localhost:3001
2. Crie uma conta de administrador
3. Conecte ao banco de dados com as credenciais:

| Campo | Valor |
|---|---|
| Tipo | PostgreSQL |
| Host | `postgres` |
| Porta | `5432` |
| Database | `bi_platform` |
| Usuário | `postgres` |
| Senha | `postgres` |

### Dashboards Sugeridos

- **Visão Geral de Vendas** — Receita, pedidos, ticket médio
- **Análise de Clientes** — Distribuição por tier e região
- **Performance de Produtos** — Top produtos e categorias
- **Sazonalidade** — Vendas por dia da semana/mês

### Alertas

Configure alertas no Metabase para monitorar:
- Queda abrupta de vendas (>20% vs dia anterior)
- Estoque baixo (< 5 unidades)
- Pico de cancelamentos (>10% no dia)

## Exemplos de Consultas SQL

### Vendas por período

```sql
SELECT
    DATE(sale_date) as day,
    SUM(final_amount) as revenue,
    COUNT(*) as orders,
    AVG(final_amount) as avg_ticket
FROM sales
WHERE status = 'completed'
  AND sale_date >= NOW() - INTERVAL '30 days'
GROUP BY DATE(sale_date)
ORDER BY day;
```

### Top clientes por receita

```sql
SELECT
    c.name,
    c.email,
    c.tier,
    COUNT(s.id) as total_orders,
    SUM(s.final_amount) as total_spent
FROM customers c
JOIN sales s ON c.id = s.customer_id
WHERE s.status = 'completed'
GROUP BY c.id, c.name, c.email, c.tier
ORDER BY total_spent DESC
LIMIT 10;
```

### Produtos mais vendidos

```sql
SELECT
    p.name,
    p.category,
    SUM(si.quantity) as units_sold,
    SUM(si.total_price) as revenue
FROM products p
JOIN sale_items si ON p.id = si.product_id
JOIN sales s ON si.sale_id = s.id
WHERE s.status = 'completed'
  AND s.sale_date >= NOW() - INTERVAL '30 days'
GROUP BY p.id, p.name, p.category
ORDER BY revenue DESC
LIMIT 10;
```

### Taxa de retenção de clientes

```sql
WITH monthly_customers AS (
    SELECT
        DATE_TRUNC('month', sale_date) as month,
        COUNT(DISTINCT customer_id) as customers
    FROM sales
    WHERE status = 'completed'
    GROUP BY DATE_TRUNC('month', sale_date)
)
SELECT
    current.month,
    current.customers as current_customers,
    previous.customers as previous_customers,
    ROUND(
        (current.customers::float / NULLIF(previous.customers, 0) - 1) * 100,
        2
    ) as retention_rate
FROM monthly_customers current
LEFT JOIN monthly_customers previous
    ON current.month = previous.month + INTERVAL '1 month'
ORDER BY current.month;
```
