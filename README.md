# SmartCart - AI-Assisted E-Commerce Prototype

This project is a complete end-to-end Data Mining implementation using the Apriori algorithm, transformed into a live e-commerce prototype ("SmartCart"). It discovers frequently bought together products and integrates these offline insights directly into a real-time web shopping experience.

## 🏗️ Architecture

The system is divided into two distinct pipelines:

1. **Offline Data Mining Pipeline (Python & Apriori)**
   - Takes historical transactions (`online_retail_II.csv`).
   - Cleans data, generates customer baskets, and applies the Apriori algorithm.
   - Extracts Frequent Itemsets and generates Association Rules.
   - Exports `strong_association_rules.csv` to be used by the live system.

2. **Online Recommendation Pipeline (FastAPI Backend + React Frontend)**
   - **Frontend:** React + Vite SPA that simulates an e-commerce store.
   - **Backend:** FastAPI connected to a local SQLite database containing the product catalog.
   - **Recommendation Engine:** When a user views a product or adds items to their cart, the backend searches the pre-computed `strong_association_rules.csv`.
   - **Discount Engine:** Evaluates the cart contents against the association rules. If complementary bundle items are present, it dynamically applies a 5%, 10%, or 15% discount based on the rule's Confidence and Lift metrics.

## 🛠️ Tech Stack
- **Data Mining:** Python, Pandas, Scipy, mlxtend
- **Backend:** FastAPI, SQLAlchemy, SQLite, Pydantic
- **Frontend:** React, Vite, TailwindCSS, React Router, Axios

## 🚀 Installation & Setup

1. **Install dependencies:**
   ```bash
   # Root Data Mining & Backend
   pip install -r requirements.txt
   pip install fastapi uvicorn sqlalchemy pydantic

   # Frontend
   cd frontend
   npm install
   ```

2. **Run the Offline Pipeline (Generate Rules):**
   ```bash
   python main.py
   ```
   *(Ensure `data/raw/online_retail_II.csv` is present).*

3. **Initialize the Database:**
   ```bash
   python -m backend.data_initializer
   ```
   *(This extracts unique products from the cleaned dataset and populates `backend/ecommerce.db`).*

4. **Start the Backend:**
   ```bash
   uvicorn backend.main:app --reload
   ```

5. **Start the Frontend:**
   ```bash
   cd frontend
   npm run dev
   ```

## 🧠 How it Works

### Apriori
The Apriori algorithm discovers itemsets that appear together frequently in historical transactions. We extract rules (e.g., `A -> B`) meaning "if a customer buys A, they are likely to buy B".
- **Support:** How often A and B are bought together overall.
- **Confidence:** Out of all times A is bought, how often is B bought?
- **Lift:** How much more likely B is bought when A is bought, compared to buying B independently. (Lift > 1 implies a positive relationship).

### Recommendations
Instead of running Apriori live on every click (which is computationally impossible for large datasets), the FastAPI backend loads the pre-computed `strong_association_rules.csv` into memory. 
- When viewing **Product A**, it searches for rules where `Antecedent == Product A` and returns the `Consequent` products.
- In the **Cart**, it checks if any subset of the cart items forms an Antecedent to suggest a "Complete Your Bundle" recommendation.

### Discounts
Discounts are business rules layered on top of the Apriori data. We assume:
- **Very Strong (Conf >= 0.70, Lift >= 2.0):** 5% bundle discount.
- **Strong (Conf >= 0.50, Lift >= 1.5):** 10% bundle discount.
- **Moderate (Conf >= 0.30, Lift >= 1.2):** 15% bundle discount.
*(Note: These are heuristic assumptions for the prototype, not profit-optimized models).*

## 🔌 API Endpoints
- `GET /api/products`: List products
- `GET /api/products/search?q=...`: Search catalog
- `GET /api/products/{id}`: Product details
- `GET /api/recommendations/{id}`: Get product-level recommendations
- `POST /api/cart/recommendations`: Get cart-level recommendations
- `GET /api/cart`: View cart and active bundle discounts
- `POST /api/cart/add`: Add item to cart
- `POST /api/cart/checkout`: Simulate placing an order

## 🛒 Demo Workflow
1. Open `http://localhost:5173`.
2. Browse or search for a product (e.g., "WHITE HANGING HEART").
3. Click the product. Observe the **"Frequently Bought Together"** section populated directly from the Apriori rules.
4. Click **"Add to Cart"** on the main product.
5. Click **"Add to Bundle"** on the recommended product.
6. Navigate to the Cart.
7. Observe the **Bundle Discount** applied automatically based on the rule's confidence/lift.
8. Click **"Proceed to Checkout"**, enter details, and place the simulated order.

## 🛑 Limitations & Future Scope
- The cart is currently session-based in memory on the backend (prototype limitation). A real system would use JWT tokens or database sessions.
- SQLite is used for simplicity; a production system would use PostgreSQL.
- Product images are placeholders since the original dataset lacks image URLs.
- Categories are absent from the original dataset and could be inferred using NLP in the future.