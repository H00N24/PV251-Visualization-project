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
</head>
<body>
"""

html_graph_template = """
<div id="vis_{class_name}"> </div>

<script type="text/javascript">
var spec = "https://raw.githubusercontent.com/H00N24/PV251-Visualization-project/master/json/{class_name}.json";
vegaEmbed('#vis_{class_name}', spec).then(function(result) {{
}}).catch(console.error);
</script>
"""


html_end = "</body>\n</html>"

results = pd.read_csv("data/classifiers-comparison.csv")

selection = alt.selection_multi(fields=["Classifier"])
brush = alt.selection(type="interval")

predicate = brush | selection

color = alt.condition(
    predicate, alt.Color("Classifier:N", legend=None), alt.value("lightgray")
)


points = (
    alt.Chart()
    .mark_point()
    .encode(
        x=alt.X("Dataset"),
        y=alt.Y("Test accuracy:Q", scale=alt.Scale(domain=(0, 1))),
        color=alt.condition(
            predicate, alt.Color("Classifier:N", legend=None), alt.value("lightgray")
        ),
        tooltip=[
            "Classifier:N",
            alt.Text("Test accuracy:Q", title="Accuracy", format=".3f"),
            "Dataset:N",
        ],
    )
    .add_selection(brush, selection)
    .properties(width=1000, height=300, title="Comparison of classifiers")
)

legend = (
    alt.Chart()
    .mark_point()
    .encode(
        y=alt.Y("Classifier:N", axis=alt.Axis(orient="right"), title=""),
        color=alt.condition(
            selection, alt.Color("Classifier:N", legend=None), alt.value("lightgray")
        ),
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
        color=alt.Color("Classifier:N", legend=None),
        tooltip=[
            "Classifier:N",
            alt.Text(
                "average(Test accuracy):Q", title="Average accuracy", format=".3f"
            ),
        ],
        x=alt.X("average(Test accuracy):Q", scale=alt.Scale(domain=(0, 1))),
    )
    .transform_filter(predicate)
    .properties(width=1000, height=200)
)

compare_chart = alt.vconcat(
    alt.hconcat(points, legend, data=results), bars, data=results
)
compare_chart.save("html/comparison.html")
compare_chart.save("json/comparison.json")

compare_chart_html = html_graph_template.format(class_name="comparison")

data_dir = "data"
data_files = [x for x in os.listdir(data_dir) if x != "classifiers-comparison.csv"]

chart_htmls = []
for data_file in data_files:
    dataframe = pd.read_csv(os.path.join(data_dir, data_file))
    name = data_file.replace(".csv", "")

    scale = alt.Scale(domain=(-0.1, 1.1))

    selection = alt.selection_multi(fields=["Class"])

    chart = (
        alt.Chart(dataframe)
        .mark_circle()
        .encode(
            x=alt.X("X:Q", title="", axis=alt.Axis(labels=False), scale=scale),
            y=alt.X("Y:Q", title="", axis=alt.Axis(labels=False), scale=scale),
            column=alt.Column("Method:N", title="Dataset: " + name),
            color=alt.condition(
                selection, alt.Color("Class:N", legend=None), alt.value("lightgray")
            ),
            tooltip=["Class:N"],
        )
        .add_selection(selection)
        .interactive()
    )

    chart_htmls.append(html_graph_template.format(class_name="dataset-" + name))
    chart.save("html/dataset-" + name + ".html")
    chart.save("json/dataset-" + name + ".json")


with open("index.html", "w") as html_file:

    html_file.write(html_start)
    html_file.write("<h1>Comparison of classifiers</h1>")
    html_file.write(compare_chart_html)
    html_file.write("<h1>Comparison of dimension reduction methods</h1>")

    for chart_html in chart_htmls:
        html_file.write(chart_html)

    html_file.write(html_end)


webbrowser.open_new_tab("index.html")
