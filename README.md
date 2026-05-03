**Data_architect.py** is a sample data Architecture challenge to yourself.  Describe your architecture and a model to OpenAI gpt 4-mini will be used.
This model will respond to by challenging things you might have not thought about or might have missed.
Deploy this to gitHub and connect your GitHub account to Streamlit IO.

**Dimensional_modeling.py** is a tool that will assist you creating your....... you guessed it, Data Modeling!  Obviously, this modeling model, shouldn't replace your ER diagram but this is a tool that can make us, DataWarehouse / Data / ML Architects, more efficient or help us with a particular we may have overlooked. It should be used in the conceptual phase.  You'll still need to do the logical and physical phase after using this. This model also uses gpt 40mini.  If you want, you can always downgrade them to gpt 3.5 turbo to lower your token cost. 

So below is sample of how it can be used:

1️⃣ **Describe the business process you want to model**
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

6️⃣ **Evaluation Mode**  
When enabled, the AI will not just record your inputs, it will also review and score your dimensional modeling decisions, providing feedback on things like grain correctness, KPIs, conformed dimension design, and overall business alignment.  
  
If you leave it disabled, the app simply collects your inputs (business process, grain, source tables, KPIs) so you can focus on building your model without being “graded” or challenged.
  
Passwords should be stored in your secrets.toml but I've set it to gitignore.  Also don't forget to set your passwords in Streamlit IO.
Also do NOT put in any data in there.  Just fill in your DDLs and metadata is all you need.  
  
**Dimensional_modeling_RAG.py** ->  I've improved the Dimensional_modeling.py to use "memorization" and Retrieval Augemented Generative and semantic search with this version.  It will do this by enabling you to store your past projects into your PineCone embedding and into SQLite database (hosted via Streamlit). The RAG will be used when it will need to find similar past data models -> inject them into your prompt -> ask GPT to design a new one using that memory"  
 - The Memory Mode option is for your RAG to be used.  It's like saying "Should I include past similar projects from Pinecone when I generate the answer?"  So check this off and then click on Start Modeling if you want to answers influenced by past similar objects.  
- Save Project -> this enables you name this project you're working on and save it for later use.
- You can Resume Project via selecing that project and then clicking Load Project.
- Semantic search projects -> Performs a semantic search for your projects.  Example, "patients insurance analytics model"
- **NOTE** --> instead of SQLite, for production, we should host it in PostGres or SQL Server.  Even though we can use Snowflake, it's not optimal since this app is going to be very OLTP-style behavior (transactional app pattern).  We don't woant unnecessary computer cost and over-engineer for simple CRUD.

Have fun!
