Data_architect.py is a sample data Architecture challenge to yourself.  Describe your architecture and a model to OpenAI gpt 4-mini will be used.
This model will respond to by challenging things you might have not thought about or might have missed.
Deploy this to gitHub and connect your GitHub account to Streamlit IO.

dimension_modeling.py is a tool that will assist you creating your... you guessed it, Data Modeling!  Obviously this shouldn't replace your ER diagram but
this is a tool that can make us DataWarehouse / Data Architects more efficient or something that we may overlooked.

So below is sample of how it can be used:

1️⃣**Describe the business process you want to model**
I need help designing a sales data model for a retail chain. 
We have daily sales data for multiple stores and products, 
including revenue, quantity, and discounts. 

I want a star schema that includes:
- Fact table: Sales transactions
- Dimensions: Date, Store, Product, Customer

Please suggest:
1. The primary keys for each table
2. How to handle surrogate vs natural keys
3. Whether I should create any accumulating snapshot tables
4. Any recommendations for efficient querying in Snowflake

2️⃣ **Define the grain:**  
- One row per product per store per day (daily sales snapshot)

3️⃣ **List the source tables:**  
- Sales_Transactions (transaction_id, store_id, product_id, customer_id, quantity, revenue, discount, date_id)  
- Stores (store_id, store_name, region, manager)  
- Products (product_id, product_name, category, price)  
- Customers (customer_id, first_name, last_name, loyalty_status)  
- Dates (date_id, date, month, quarter, year)

4️⃣ **List the KPIs or measures:**  
- Total Revenue  
- Total Quantity Sold  
- Average Discount  
- Number of Transactions  
- Customer Count

5️⃣ **Additional considerations:**  
- Suggest primary keys and surrogate keys for all tables  
- Indicate any accumulating snapshot tables needed  
- Recommend clustering keys for Snowflake to optimize queries  
- Suggest any indexes or optimization strategies

6️⃣ **for Evaluation Mode**
When enabled, the AI will not just record your inputs, it will also review and score your dimensional modeling decisions,   
providing feedback on things like grain correctness, KPIs, conformed dimension design, and overall business alignment.  
  
If you leave it disabled, the app simply collects your inputs (business process, grain, source tables, KPIs) so you can focus on building your model without being “graded” or challenged.

Have fun!
