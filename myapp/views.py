from django.conf import settings
from django.shortcuts import render
from django.core.files.storage import FileSystemStorage
import pandas as pd
import plotly.express as px
import os
import random

def safe_read_file(file_path, file_extension):
    """Safely read files with automatic encoding detection"""
    encodings = ['utf-8', 'utf-8-sig', 'latin1', 'cp1252', 'iso-8859-1']
    
    for encoding in encodings:
        try:
            if file_extension == ".csv":
                return pd.read_csv(file_path, encoding=encoding)
            elif file_extension == ".xlsx":
                return pd.read_excel(file_path)
            elif file_extension == ".json":
                with open(file_path, 'r', encoding=encoding) as f:
                    return pd.read_json(f.read())
        except:
            continue
    
    try:
        if file_extension == ".csv":
            return pd.read_csv(file_path, encoding='latin1', encoding_errors='replace')
    except:
        pass
    
    raise Exception("Cannot read file")

def index(request):
    result = None
    chart = None
    df = None

    if request.method == "POST":
        # FILE UPLOAD ✅
        if request.FILES.get("file"):
            uploaded_file = request.FILES["file"]
            fs = FileSystemStorage(location=settings.MEDIA_ROOT)
            filename = fs.save(uploaded_file.name, uploaded_file)
            file_path = fs.path(filename)
            
            request.session["file_path"] = file_path
            
            try:
                if filename.endswith(".csv"):
                    df = safe_read_file(file_path, ".csv")
                elif filename.endswith(".xlsx"):
                    df = pd.read_excel(file_path)
                elif filename.endswith(".json"):
                    df = safe_read_file(file_path, ".json")
                else:
                    result = "❌ Unsupported file format!"
                    df = None
                
                if df is not None:
                    result = f"✅ File uploaded: {len(df)} rows, {len(df.columns)} columns"
                    
            except Exception as e:
                result = f"❌ File error: {str(e)[:100]}"

        # NLP QUERY ✅ MOCK ANALYSIS (WORKS WITHOUT OpenAI!)
        if request.POST.get("query"):
            query = request.POST.get("query").strip().lower()
            file_path = request.session.get("file_path")

            if file_path and os.path.exists(file_path) and query:
                try:
                    if file_path.endswith(".csv"):
                        df = safe_read_file(file_path, ".csv")
                    elif file_path.endswith(".xlsx"):
                        df = pd.read_excel(file_path)
                    elif file_path.endswith(".json"):
                        df = safe_read_file(file_path, ".json")
                except Exception as e:
                    result = f"❌ Cannot read file: {str(e)}"
                    df = None

                if df is not None and len(df) > 0:
                    # 🔥 SMART MOCK ANALYSIS BASED ON QUERY
                    cols = df.columns.tolist()
                    
                    if any(word in query for word in ['chart', 'graph', 'plot', 'visual']):
                        # Generate random chart
                        if len(cols) >= 2:
                            x_col, y_col = cols[0], cols[1]
                            if df[x_col].dtype in ['int64', 'float64']:
                                fig = px.bar(df.head(10), x=x_col, y=y_col, title=f"{y_col} by {x_col}")
                            else:
                                fig = px.pie(df.head(10), names=x_col, values=y_col, title=f"{y_col} Distribution")
                            chart = fig.to_html(full_html=False, include_plotlyjs=True)
                            result = f"✅ Chart: {y_col} by {x_col}"
                        else:
                            result = "✅ Need 2+ columns for charts"
                            
                    elif any(word in query for word in ['top', 'largest', 'highest', 'max']):
                        top = df.nlargest(10, cols[0])[cols[:3]].to_string()
                        result = f"✅ Top 10 by {cols[0]}:\n{top}"
                        
                    elif any(word in query for word in ['summary', 'stats', 'describe']):
                        result = f"✅ Dataset Summary:\n{df.describe().to_string()}"
                        
                    elif any(word in query for word in ['head', 'first', 'sample']):
                        result = f"✅ First 5 rows:\n{df.head().to_string()}"
                        
                    else:
                        # Default analysis
                        summary = f"""
✅ AI Data Analysis Complete! 📊
Columns: {', '.join(cols[:5])}{'...' if len(cols)>5 else ''}
Rows: {len(df)}
Sample: {df.iloc[0].to_dict()}

💡 Try queries like:
• "show chart"
• "top 10 values" 
• "summary statistics"
• "first 5 rows"
                        """
                        result = summary

    return render(request, "index.html", {
        "result": result, 
        "chart": chart,
        "df": df,
        "has_file": bool(request.session.get("file_path"))
    })
