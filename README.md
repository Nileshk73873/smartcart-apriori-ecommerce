# SmartCart - AI-Assisted E-Commerce & Association Rule Mining Platform

An end-to-end Data Warehousing & Data Mining (DWM) project featuring offline transaction mining with the **Apriori Algorithm**, an **Interactive Streamlit Analytics Dashboard**, a **FastAPI backend** with JWT authentication and dynamic bundle discount logic, and an **Amazon-style React (Vite) E-Commerce Web Application**.

---

## 📑 Table of Contents
- [Architecture Overview](#-architecture-overview)
- [Key Features](#-key-features)
- [Tech Stack](#️-tech-stack)
- [Installation & Setup](#-installation--setup)
- [Running the Application](#-running-the-application)
- [How It Works (Apriori, Recommendations & Discounts)](#-how-it-works)
- [API Reference](#-api-reference)
- [Testing & Quality Assurance](#-testing--quality-assurance)
- [Project Directory Structure](#-project-directory-structure)

---

## 🏗️ Architecture Overview

The platform consists of three core layers:

```
┌─────────────────────────────────────────────────────────────┐
│ 1. Offline Data Mining & Preprocessing Pipeline (Python)    │
│    • Cleans 1,067,371 rows of Online Retail II logs         │
│    • Builds sparse transaction baskets                      │
│    • Mines Frequent Itemsets & High-Lift Association Rules  │
│    • Generates Pre-computed Bundles & Discount Tiers        │
└──────────────────────────────┬──────────────────────────────┘
                               │
            ┌──────────────────┴──────────────────┐
            ▼                                     ▼
┌──────────────────────────────┐    ┌──────────────────────────────┐
│ 2. Streamlit Analytics App   │    │ 3. Full-Stack E-Commerce     │
│    • Diagnostic EDA & Stats  │    │    • FastAPI Backend API     │
│    • Scatter & Network plots │    │    • JWT Auth & Admin Panel  │
│    • Pricing Simulator       │    │    • SQLite DB (5,335 items) │
│    • Academic Defense Guide  │    │    • React + Tailwind Web App│
└──────────────────────────────┘    └──────────────────────────────┘
```

1. **Offline Data Mining Pipeline (`main.py` / `src/`):**
   - Cleans the raw Online Retail II dataset (`data/raw/online_retail_II.csv`).
   - Generates binary sparse transaction basket matrices.
   - Computes Frequent Itemsets and Association Rules using `mlxtend` with configurable Support, Confidence, and Lift.
   - Produces output CSVs: `cleaned_retail.csv`, `frequent_itemsets.csv`, `strong_association_rules.csv`, and `bundle_recommendations.csv`.

2. **Interactive Streamlit Dashboard (`app.py`):**
   - Real-time parameter tuning (Min Support, Confidence, Lift).
   - Interactive Plotly visualizations (Support vs Confidence, Confidence vs Lift, Basket size distributions, Top products).
   - Interactive Bundle Price & Customer Savings Simulator.
   - Viva & Academic Defense preparation guide.

3. **Live E-Commerce Web Application (`backend/` & `frontend/`):**
   - **Frontend:** React SPA built with Vite, TailwindCSS, and Lucide icons featuring Amazon-style layout, product filters, cart management, and order tracking.
   - **Backend:** FastAPI with SQLite, JWT authentication, role-based access control (Admin vs Customer), and dynamic cart discounting.
   - **Recommendation Engine:** 3-stage matching (Antecedent matching → Consequent/Complement matching → High-Lift Trending fallback) ensuring non-empty recommendations for every product and cart state.

---

## 🌟 Key Features

* **Real-World Apriori Implementation:** Mines transaction affinity across 39,500+ shopping baskets and 5,300+ unique products.
* **Tiered Bundle Discount Engine:** Automatically applies tiered discounts (5% to 15%) when complementary items from a rule are added to the cart:
  * **Very Strong (Confidence ≥ 0.70, Lift ≥ 2.0):** 5% bundle discount (High organic affinity).
  * **Strong (Confidence ≥ 0.50, Lift ≥ 1.5):** 10% bundle discount (Moderate cross-sell incentive).
  * **Moderate (Confidence ≥ 0.30, Lift ≥ 1.2):** 15% bundle discount (Margin-safe promotional trigger).
* **Frequently Bought Together Cross-Sells:** Product detail pages and cart pages display recommended complementary items with lift metrics.
* **Full Authentication & Admin Portal:**
  * JWT-based login and signup.
  * Admin dashboard (`/admin`) for managing Users, Orders, Order Statuses, and Products.
  * Customer order history with return management (`/orders`).
* **Isolated Carts:** User-specific authenticated carts with seamless fallback for guest sessions.

---

## 🛠️ Tech Stack

* **Data Mining & Analytics:** Python 3.11+, Pandas, NumPy, SciPy, Mlxtend, Plotly, Streamlit
* **Backend:** FastAPI, SQLAlchemy, SQLite, Pydantic, PyJWT, Bcrypt, Uvicorn
* **Frontend:** React 18, Vite, TailwindCSS, React Router 6, Axios, Lucide React
* **Testing:** Pytest, AnyIO, Starlette TestClient

---

## 🚀 Installation & Setup

### Prerequisites
* Python 3.10+ installed
* Node.js 18+ and npm installed
* Dataset: Ensure `data/raw/online_retail_II.csv` is present in the project root.

### 1. Python Environment & Dependencies
```bash
# Clone or open the repository
cd smartcart-apriori-ecommerce

# Install root dependencies
pip install -r requirements.txt
```

### 2. Frontend Dependencies
```bash
cd frontend
npm install
cd ..
```

---

## 🏃 Running the Application

### Step 1: Run the Apriori Mining Pipeline
Run the offline data mining script to process raw transactions and generate association rules:
```bash
python main.py
```
*Generated artifacts will be saved in `data/processed/` and `outputs/`.*

### Step 2: Initialize SQLite Database & Seed Products
Extract unique catalog items from the processed dataset and populate `backend/ecommerce.db`:
```bash
python -m backend.data_initializer
```

### Step 3: Create Default Admin User (Optional)
Create or reset an administrator account (`admin` / `admin123`):
```bash
python create_admin.py
```

### Step 4: Start the FastAPI Backend
```bash
uvicorn backend.main:app --reload --port 8000
```
*API Swagger Documentation will be live at `http://localhost:8000/docs`.*

### Step 5: Start the React Frontend
In a separate terminal:
```bash
cd frontend
npm run dev
```
*The web store will be available at `http://localhost:5173`.*

### Step 6: Launch Streamlit Analytics Dashboard (Optional)
In a separate terminal:
```bash
streamlit run app.py
```
*The dashboard will open at `http://localhost:8501`.*

---

## 🧠 How It Works

### Association Rule Mining Metrics
For an association rule $A \rightarrow B$:
* **Support:** $P(A \cap B)$ — Proportion of transactions containing both $A$ and $B$.
* **Confidence:** $P(B \mid A) = \frac{P(A \cap B)}{P(A)}$ — Probability of buying $B$ given that $A$ was purchased.
* **Lift:** $\frac{P(A \cap B)}{P(A) \cdot P(B)}$ — Co-occurrence ratio over random chance. A Lift $> 1.0$ indicates positive correlation.

### Intelligent 3-Stage Recommendation Logic
1. **Direct Antecedent Match:** Finds rules where the item in the cart or product page is in the antecedent set ($A \rightarrow B$), recommending consequent $B$.
2. **Complementary Inverse Match:** Finds rules where the product is in the consequent set ($B \leftarrow A$), recommending antecedent $A$.
3. **Trending Bundle Fallback:** If an infrequent product has no direct rules, surfaces top high-lift global rules from the Apriori model to prevent empty recommendations.

### Dynamic Cart Discounting Logic
When viewing the cart (`/cart`) or checking out:
* The backend inspects all items in the cart against active rules in `outputs/strong_association_rules.csv`.
* If a full bundle is present, the discount percentage is applied **strictly to the line total of items forming the bundle** (protecting margins on non-bundle items).

---

## 🔌 API Reference

| Method | Endpoint | Description | Auth Required |
|---|---|---|---|
| `GET` | `/api/products` | Fetch paginated product catalog | No |
| `GET` | `/api/products/search?q={query}` | Search catalog by keyword | No |
| `GET` | `/api/products/{id}` | Get product details | No |
| `GET` | `/api/recommendations/{id}` | Product-level association recommendations | No |
| `POST` | `/api/cart/recommendations` | Cart-level complementary recommendations | No |
| `GET` | `/api/cart/` | Get current cart with applied discounts | No (Session/Auth) |
| `POST` | `/api/cart/add` | Add item to cart | No (Session/Auth) |
| `PUT` | `/api/cart/update` | Update item quantity | No (Session/Auth) |
| `DELETE` | `/api/cart/remove/{id}` | Remove item from cart | No (Session/Auth) |
| `POST` | `/api/cart/checkout` | Place order | No (Session/Auth) |
| `POST` | `/api/auth/signup` | Register a new customer account | No |
| `POST` | `/api/auth/login` | Login and retrieve JWT access token | No |
| `GET` | `/api/auth/me` | Fetch currently logged-in user profile | Yes |
| `GET` | `/api/cart/orders` | Fetch authenticated user's order history | Yes |
| `POST` | `/api/cart/orders/{id}/return` | Submit return request for an order | Yes |
| `GET` | `/api/admin/users` | List all registered users (Admin only) | Admin |
| `GET` | `/api/admin/orders` | List and manage all customer orders | Admin |
| `PUT` | `/api/admin/orders/{id}/status` | Update order processing status | Admin |

---

## 🧪 Testing & Quality Assurance

Run the comprehensive unit and integration test suite:

```bash
pytest -v
```

### Test Coverage Includes:
* `test_preprocessing.py`: Validation of cancelled invoice filtering, negative price/quantity cleaning, and date parsing.
* `test_basket.py`: Sparse matrix integrity and transaction aggregation verification.
* `test_rules.py`: Mathematical correctness of hand-calculated Support, Confidence, and Lift.
* `test_recommendations.py`: Product and bundle recommendation ranking and formatting.
* `test_cart_discount.py`: Verifies discount applies strictly to bundle items and never to incomplete sets.
* `test_backend_auth.py`: Token validation, guest vs authenticated cart isolation, and admin RBAC enforcement.

---

## 📁 Project Directory Structure

```text
smartcart-apriori-ecommerce/
├── backend/
│   ├── admin.py               # Admin portal routes & management
│   ├── auth.py                # JWT authentication & password hashing
│   ├── cart.py                # Cart operations & discount evaluator
│   ├── database.py            # SQLAlchemy database engine & sessions
│   ├── data_initializer.py    # Database seeder from cleaned CSV
│   ├── main.py                # FastAPI app initialization & routing
│   ├── models.py              # SQLAlchemy ORM models (User, Product, Order)
│   ├── products.py            # Product search & pagination endpoints
│   ├── recommendations.py     # Live Apriori recommendation handlers
│   └── schemas.py             # Pydantic request & response schemas
├── data/
│   ├── raw/                   # Raw retail CSVs (online_retail_II.csv)
│   └── processed/             # Cleaned transaction records (cleaned_retail.csv)
├── frontend/
│   ├── src/
│   │   ├── components/        # Navbar, Footer, UI widgets
│   │   ├── context/           # AuthContext & global state
│   │   ├── pages/             # Home, Cart, Checkout, Orders, ProductDetail, Admin
│   │   ├── api.js             # Axios client with JWT interceptor
│   │   └── App.jsx            # React Router routing setup
│   └── package.json
├── outputs/                   # Apriori generated CSVs (rules, bundles, itemsets)
├── src/
│   ├── basket.py              # Sparse binary basket matrix builder
│   ├── discount.py            # Discount tier business rules
│   ├── eda.py                 # Exploratory data analysis utilities
│   ├── preprocessing.py       # Retail log cleaning pipeline
│   ├── recommendations.py     # Core recommendation & bundling functions
│   └── rules.py               # Apriori execution & association rule miners
├── tests/                     # 23 Automated pytest suites
├── app.py                     # Interactive Streamlit analytics dashboard
├── create_admin.py            # Admin user provisioning script
├── main.py                    # Apriori CLI pipeline entrypoint
├── requirements.txt           # Python dependency specifications
└── README.md                  # System documentation
```