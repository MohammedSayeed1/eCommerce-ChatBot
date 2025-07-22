from flask import Flask, request, jsonify, render_template
from flask_cors import CORS
from sqlalchemy import create_engine, text
from google import genai
import os

os.environ["GEMINI_API_KEY"] = "API_KEY(due to security reasons, I have removed it.)"

client = genai.Client()

app = Flask(__name__)
CORS(app)

engine = create_engine("sqlite:///ecommerce.db")

def generate_sql_with_gemini(question):
    prompt = f"""
You are a helpful and interactive SQL data analyst. When a user asks a question, first explain how you're interpreting the request, then show the SQL query that answers it.

Available tables:
- Ad_sales(date, item_id, ad_sales, impressions, ad_spend, clicks, units_sold)
- Total_sales(date, item_id, total_sales, total_units_ordered)
- Eligibility(eligibility_datetime_utc, item_id, eligibility, message)

For each question:
- First provide a brief explanation in plain English.
- Then output the SQL query on a new line.
- Be conversational and clear.

Question: {question}
"""
    try:
        response = client.models.generate_content(
            model="gemini-2.5-flash",
            contents=prompt
        )
        full_reply = response.text.strip()

        # Extract SQL by looking for the first code block
        if "```sql" in full_reply:
            sql_part = full_reply.split("```sql")[1].split("```")[0].strip()
        else:
            # fallback if Gemini didn't use markdown format
            lines = full_reply.splitlines()
            sql_lines = [line for line in lines if line.strip().upper().startswith("SELECT")]
            sql_part = "\n".join(sql_lines).strip()

        return full_reply, sql_part  # return both explanation and query

    except Exception as e:
        print("Gemini error:", e)
        raise

@app.route('/')
def index():
    return render_template('index.html')  # Your frontend HTML must be in the 'templates' folder

@app.route("/ask", methods=["POST"])
def ask():
    try:
        data = request.get_json()
        question = data.get("question", "")
        print("User question:", question)

        explanation_and_sql, sql_query = generate_sql_with_gemini(question)
        print("Generated SQL:", sql_query)

        with engine.connect() as conn:
            result = conn.execute(text(sql_query))
            rows = [dict(row) for row in result.mappings()]


        print("Query result:", rows)

        return jsonify({
            "explanation": explanation_and_sql,
            "sql": sql_query,
            "results": rows
        })

    except Exception as e:
        print("Error:", e)
        return jsonify({"error": str(e)}), 500

# === Run Flask App ===
if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5550, debug=True)
