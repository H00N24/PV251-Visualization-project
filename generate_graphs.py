#!/usr/bin/env python3
import os
import webbrowser

import altair as alt
import pandas as pd

html_start = """
<!DOCTYPE html>
<head>
  <meta charset="utf-8">
  <script src="https://cdn.jsdelivr.net/npm/vega@5"></script>
    <script src="https://cdn.jsdelivr.net/npm/vega-lite@3"></script>
    <script src="https://cdn.jsdelivr.net/npm/vega-embed@4"></script>
<style>
body {font-family: Arial, Helvetica, sans-serif;}

.modal {
  display: none;
  position: fixed;
  z-index: 1;
  padding-top: 100px;
  left: 0;
  top: 0;
  width: 100%;
  height: 100%;
  overflow: auto; 
  background-color: rgb(0,0,0); 
  background-color: rgba(0,0,0,0.4);
}

.modal-content {
  background-color: #fefefe;
  margin: auto;
  padding: 20px;
  border: 1px solid #888;
  width: 80%;
}

.close {
  color: #aaaaaa;
  float: right;
  font-size: 28px;
  font-weight: bold;
}

.close:hover,
.close:focus {
  color: #000;
  text-decoration: none;
  cursor: pointer;
}

.button {
  background-color: #4CAF50; /* Green */
  border: none;
  color: white;
  padding: 15px 32px;
  text-align: center;
  text-decoration: none;
  display: inline-block;
  font-size: 16px;
}

.grid-container {
  display: grid;
  grid-template-columns: auto auto auto auto auto auto;
  padding: 10px;
  grid-row-gap: 10px;
  grid-column-gap: 10px;
}
.grid-item {
  background-color: #4CAF50; /* Green */
  border: none;
  color: white;
  padding: 15px 32px;
  text-align: center;
  text-decoration: none;
  display: inline-block;
  font-size: 16px;
}

h1 {
    text-align:center;
}
.loader {
    display: inline-block;  
  border: 16px solid #f3f3f3;
  border-radius: 50%;
  border-top: 16px solid #3498db;
  width: 120px;
  height: 120px;
  -webkit-animation: spin 2s linear infinite; /* Safari */
  animation: spin 2s linear infinite;
}

/* Safari */
@-webkit-keyframes spin {
  0% { -webkit-transform: rotate(0deg); }
  100% { -webkit-transform: rotate(360deg); }
}

@keyframes spin {
  0% { transform: rotate(0deg); }
  100% { transform: rotate(360deg); }
}
</style>

</head>
<body>
"""

html_comparison_graph_template = """
<div id="vis_{class_name}" style="text-align:center;"> <div class="loader"></div> </div>

<script type="text/javascript">
var spec = "https://raw.githubusercontent.com/H00N24/PV251-Visualization-project/master/json/{class_name}.json";
vegaEmbed('#vis_{class_name}', spec).then(function(result) {{
}}).catch(console.error);
</script>
"""


html_graph_template = """
<div class="grid-item">
    <button class="button" id="btn_{class_name}">{class_name}</button>
    <div id="modal_{class_name}" class="modal">
        <div class="modal-content" >
            <div id="vis_{class_name}" style="text-align:center;"><div class="loader"></div> </div>
        </div>
    </div>

    <script type="text/javascript">
var spec = "https://raw.githubusercontent.com/H00N24/PV251-Visualization-project/master/json/dataset-{class_name}.json";
vegaEmbed('#vis_{class_name}', spec).then(function(result) {{
}}).catch(console.error);


var modal = document.getElementById("modal_{class_name}");
var btn = document.getElementById("btn_{class_name}");

btn.onclick = function() {{
modal.style.display = "block";
}}


window.onclick = function(event) {{
if (event.target == modal) {{
    modal.style.display = "none";
}}
}}
    </script>
</div>
"""


html_end = "</div></body>\n</html>"

results = pd.read_csv("data/classifiers-comparison.csv")

selection = alt.selection_multi(fields=["Classifier"])

domain = results["Classifier"].unique()
range_ = [
    "#e6194b",
    "#3cb44b",
    "#4363d8",
    "#f58231",
    "#911eb4",
    "#46f0f0",
    "#f032e6",
    "#bcf60c",
    "#fabebe",
    "#008080",
    "#e6beff",
    "#9a6324",
    "#800000",
    "#aaffc3",
    "#808000",
    "#000075",
]

scale = alt.Scale(domain=domain.tolist(), range=range_)


color = alt.condition(
    selection,
    alt.Color("Classifier:N", legend=None, scale=scale),
    alt.value("lightgray"),
)
opacity = alt.condition(selection, alt.value(1), alt.value(0.2))


points = (
    alt.Chart()
    .mark_line(point=True)
    .encode(
        x=alt.X("Dataset"),
        y=alt.Y("Test accuracy:Q", scale=alt.Scale(domain=(0, 1))),
        color=color,
        opacity=opacity,
        tooltip=[
            "Classifier:N",
            alt.Text("Test accuracy:Q", title="Accuracy", format=".3f"),
            "Dataset:N",
        ],
    )
    .add_selection(selection)
    .properties(width=1000, height=300, title="Comparison of classifiers")
)

legend = (
    alt.Chart()
    .mark_point()
    .encode(
        y=alt.Y("Classifier:N", axis=alt.Axis(orient="right"), title=""), color=color
    )
    .add_selection(selection)
    .properties(title="Classifier")
)

bars = (
    alt.Chart()
    .mark_bar()
    .encode(
        y=alt.Y(
            "Classifier:N",
            sort=alt.EncodingSortField(
                field="Test accuracy", op="mean", order="descending"
            ),
            title="",
        ),
        color=color,
        tooltip=[
            "Classifier:N",
            alt.Text(
                "average(Test accuracy):Q", title="Average accuracy", format=".3f"
            ),
        ],
        x=alt.X("average(Test accuracy):Q", scale=alt.Scale(domain=(0, 1))),
    )
    .add_selection(selection)
    .properties(width=1000, height=200)
)

compare_chart = alt.vconcat(
    alt.hconcat(points, legend, data=results), bars, data=results
)
# compare_chart.save("html/comparison.html")
compare_chart.save("json/comparison.json")

compare_chart_html = html_comparison_graph_template.format(class_name="comparison")

data_dir = "data"
data_files = [x for x in os.listdir(data_dir) if x != "classifiers-comparison.csv"]

chart_htmls = []
for data_file in data_files:
    dataframe = pd.read_csv(os.path.join(data_dir, data_file))
    name = data_file.replace(".csv", "")

    scale = alt.Scale(domain=(-0.1, 1.1))

    selection = alt.selection_multi(fields=["Class"])
    color = alt.condition(
        selection,
        alt.Color("Class:N", legend=None, scale=alt.Scale(range=range_)),
        alt.value("lightgray"),
    )
    opacity = alt.condition(selection, alt.value(1), alt.value(0.2))
    chart = (
        alt.Chart(dataframe)
        .mark_circle()
        .encode(
            x=alt.X("X:Q", title="", axis=alt.Axis(labels=False), scale=scale),
            y=alt.X("Y:Q", title="", axis=alt.Axis(labels=False), scale=scale),
            column=alt.Column("Method:N", title="Dataset: " + name),
            color=color,
            opacity=opacity,
            tooltip=["Class:N"],
        )
        .add_selection(selection)
        .interactive()
    )

    chart_htmls.append(html_graph_template.format(class_name=name))
    # chart.save("html/dataset-" + name + ".html")
    chart.save("json/dataset-" + name + ".json")


with open("index.html", "w") as html_file:

    html_file.write(html_start)
    html_file.write("<h1>Comparison of classifiers</h1>")
    html_file.write(compare_chart_html)
    html_file.write("<h1>Comparison of dimension reduction methods</h1>")
    html_file.write('<div  class="grid-container">\n')

    for chart_html in chart_htmls:
        html_file.write(chart_html)

    html_file.write(html_end)


webbrowser.open_new_tab("index.html")
