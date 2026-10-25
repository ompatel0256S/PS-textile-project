
from flask import Flask, render_template, jsonify
import pandas as pd
import numpy as np

app = Flask(__name__)

# Textile dataset
DATA = [
    ["01-01-2026","Morning","M01","Polyester",12450,312,"Colour Variation",31.2,68],
    ["01-01-2026","Evening","M02","Polyester",11980,405,"Stain",32.5,71],
    ["02-01-2026","Morning","M01","Georgette",12700,285,"Hole",30.8,66],
    ["02-01-2026","Evening","M03","Rayon",11650,510,"Broken Yarn",33.1,73],
    ["03-01-2026","Morning","M02","Polyester",12100,365,"Uneven Weaving",32.0,70],
    ["03-01-2026","Evening","M03","Georgette",11850,240,"Stain",30.5,65],
    ["04-01-2026","Morning","M01","Polyester",12350,278,"Colour Variation",30.9,67],
    ["04-01-2026","Evening","M02","Rayon",11780,420,"Stain",32.4,70],
    ["05-01-2026","Morning","M03","Georgette",12050,295,"Hole",31.1,68],
    ["05-01-2026","Evening","M01","Polyester",12500,350,"Uneven Weaving",32.6,72],
    ["06-01-2026","Morning","M02","Rayon",11950,380,"Stain",30.7,66],
    ["06-01-2026","Evening","M03","Polyester",12200,460,"Colour Variation",32.3,71],
    ["07-01-2026","Morning","M01","Rayon",12300,260,"Broken Yarn",30.4,65],
    ["07-01-2026","Evening","M02","Georgette",11800,430,"Hole",31.9,69]
]

COLUMNS = [
    "Date", "Shift", "Machine_ID", "Fabric_Type",
    "Production_Meters", "Defective_Meters",
    "Defect_Type", "Temperature", "Humidity"
]


def get_data():
    df = pd.DataFrame(DATA, columns=COLUMNS)

    df["Date"] = pd.to_datetime(
        df["Date"], format="%d-%m-%Y"
    )

    df["Defect_Rate"] = (
        df["Defective_Meters"]
        / df["Production_Meters"] * 100
    )

    return df


@app.route("/")
def home():
    df = get_data()

    rows = df.copy()
    rows["Date"] = rows["Date"].dt.strftime("%d-%m-%Y")
    rows = rows.round(3).to_dict("records")

    summary = {
        "records": len(df),
        "production": int(df["Production_Meters"].sum()),
        "defective": int(df["Defective_Meters"].sum()),
        "defect_rate": round(
            df["Defective_Meters"].sum()
            / df["Production_Meters"].sum() * 100, 3
        )
    }

    return render_template(
        "index.html",
        rows=rows,
        summary=summary
    )


@app.route("/api/calculate/<topic>")
def calculate(topic):
    df = get_data()
    n = len(df)

    x = df["Production_Meters"]
    mean = x.mean()

    result = {
        "title": topic,
        "formula": "",
        "answer": "",
        "steps": [],
        "labels": [],
        "values": [],
        "graph_title": "",
        "note": ""
    }

    # 1. Original data
    if topic == "data":
        result["formula"] = "Original textile dataset"
        result["answer"] = f"{n} records"
        result["steps"] = [
            "Dataset mein 14 production records hain.",
            "Har record mein production, defective meters, "
            "machine, shift aur environmental data hai."
        ]

    # 2. Mean
    elif topic == "mean":
        result["formula"] = "Mean = Sum of values / N"
        result["answer"] = f"{mean:.2f} meters"
        result["steps"] = [
            f"Total production = {x.sum():,.0f} meters",
            f"Total observations N = {n}",
            f"Mean = {x.sum():,.0f} / {n} = {mean:.2f}"
        ]

    # 3. Median
    elif topic == "median":
        result["formula"] = "Median = Middle value(s) of sorted data"
        result["answer"] = f"{x.median():,.2f} meters"
        result["steps"] = [
            "Production values ko ascending order mein arrange karo.",
            "14 observations hain, isliye 7th aur 8th values ka "
            "average median hoga.",
            f"Median = {x.median():,.2f} meters"
        ]

    # 4. Mode
    elif topic == "mode":
        result["formula"] = "Mode = Most frequently occurring value"
        result["answer"] = "No unique mode"
        result["steps"] = [
            "Har production value ki frequency check karo.",
            "Is dataset mein production values repeat nahi hoti.",
            "Isliye koi unique mode nahi hai."
        ]

    # 5. Population variance
    elif topic == "variance":
        variance = x.var(ddof=0)
        result["formula"] = "Population variance = Sum((x - mean)^2) / N"
        result["answer"] = f"{variance:,.2f} meters squared"
        result["steps"] = [
            f"Mean = {mean:,.2f}",
            f"Squared deviations ka sum = "
            f"{((x - mean) ** 2).sum():,.2f}",
            f"Variance = {variance:,.2f}"
        ]

    # 6. Standard deviation
    elif topic == "sd":
        variance = x.var(ddof=0)
        sd = x.std(ddof=0)
        result["formula"] = "Population SD = Square root of variance"
        result["answer"] = f"{sd:,.2f} meters"
        result["steps"] = [
            f"Mean = {mean:,.2f}",
            f"Population variance = {variance:,.2f}",
            f"SD = sqrt({variance:,.2f}) = {sd:,.2f}"
        ]

    # 7. Overall defect rate
    elif topic == "defect_rate":
        total_p = df["Production_Meters"].sum()
        total_d = df["Defective_Meters"].sum()
        rate = total_d / total_p * 100

        result["formula"] = (
            "Defect rate = Total defective meters "
            "/ Total production meters * 100"
        )
        result["answer"] = f"{rate:.3f}%"
        result["steps"] = [
            f"Total production = {total_p:,.0f} meters",
            f"Total defective = {total_d:,.0f} meters",
            f"Defect rate = {total_d:,.0f} / "
            f"{total_p:,.0f} * 100 = {rate:.3f}%"
        ]

    # 8. Group analysis
    elif topic in ["machine", "shift", "fabric", "defect_type"]:
        columns = {
            "machine": "Machine_ID",
            "shift": "Shift",
            "fabric": "Fabric_Type",
            "defect_type": "Defect_Type"
        }

        col = columns[topic]

        grouped = df.groupby(col).agg(
            production=("Production_Meters", "sum"),
            defective=("Defective_Meters", "sum")
        )

        grouped["rate"] = (
            grouped["defective"] / grouped["production"] * 100
        )

        result["formula"] = (
            "Group defect rate = Group defective meters "
            "/ Group production meters * 100"
        )
        result["answer"] = f"{len(grouped)} groups analysed"
        result["steps"] = [
            f"Records ko {col} ke basis par group kiya.",
            "Har group ka total production aur defective meters sum kiya.",
            "Har group ki defect percentage calculate ki."
        ]
        result["labels"] = grouped.index.astype(str).tolist()
        result["values"] = grouped["rate"].round(3).tolist()
        result["graph_title"] = f"Defect rate by {col}"

    # 9. Probability: defect rate above 3%
    elif topic == "prob_gt3":
        count = int((df["Defect_Rate"] > 3).sum())
        probability = count / n

        result["formula"] = "P(A) = Favourable records / Total records"
        result["answer"] = f"{probability:.4f} = {probability * 100:.2f}%"
        result["steps"] = [
            "Har row ka defect rate calculate karo.",
            f"3% se zyada defect rate wali rows = {count}",
            f"Total rows = {n}",
            f"P(defect rate > 3%) = {count}/{n} = "
            f"{probability:.4f}"
        ]
        result["labels"] = ["Rate <= 3%", "Rate > 3%"]
        result["values"] = [n - count, count]
        result["graph_title"] = "Records by defect-rate threshold"

    # 10. Bayes' theorem
    elif topic == "bayes":
        df["High_Defect"] = df["Defect_Rate"] > 3

        total_high = int(df["High_Defect"].sum())
        m02_high = int(
            ((df["Machine_ID"] == "M02") & df["High_Defect"]).sum()
        )

        if total_high:
            probability = m02_high / total_high
        else:
            probability = 0

        result["formula"] = (
            "P(M02 | High defect) = "
            "P(High defect | M02) * P(M02) / P(High defect)"
        )
        result["answer"] = (
            f"{probability:.4f} = {probability * 100:.2f}%"
        )
        result["steps"] = [
            f"Rows with defect rate > 3% = {total_high}",
            f"M02 rows with defect rate > 3% = {m02_high}",
            f"P(M02 | High defect) = {m02_high}/{total_high}"
            if total_high else "No high-defect rows were found.",
            "Yahan each production row ko one observation maana gaya hai."
        ]
        result["labels"] = ["M02 and high defect", "All high-defect rows"]
        result["values"] = [m02_high, total_high]
        result["graph_title"] = "Bayes theorem: row counts"
        result["note"] = (
            "This estimates the probability that a recorded row belongs "
            "to M02 given its defect rate is above 3%. It is not an "
            "item-level defect probability."
        )

    # 11. Conditional probability
    elif topic == "conditional":
        evening = df[df["Shift"] == "Evening"]
        stain = evening[
            evening["Defect_Type"].str.lower() == "stain"
        ]

        probability = len(stain) / len(evening)

        result["formula"] = (
            "P(Stain | Evening) = Evening Stain rows / Evening rows"
        )
        result["answer"] = (
            f"{probability:.4f} = {probability * 100:.2f}%"
        )
        result["steps"] = [
            f"Evening records = {len(evening)}",
            f"Evening records labelled Stain = {len(stain)}",
            f"P(Stain | Evening) = {len(stain)}/{len(evening)}"
        ]
        result["labels"] = ["Stain", "Other defect types"]
        result["values"] = [len(stain), len(evening) - len(stain)]
        result["graph_title"] = "Evening shift defect categories"

    # 12. Total probability
    elif topic == "total_probability":
        morning = df[df["Shift"] == "Morning"]
        evening = df[df["Shift"] == "Evening"]

        p_morning = len(morning) / n
        p_evening = len(evening) / n

        p_hole_morning = (
            morning["Defect_Type"].str.lower() == "hole"
        ).sum() / len(morning)

        p_hole_evening = (
            evening["Defect_Type"].str.lower() == "hole"
        ).sum() / len(evening)

        p_hole = (
            p_hole_morning * p_morning
            + p_hole_evening * p_evening
        )

        result["formula"] = (
            "P(Hole) = P(Hole|Morning)P(Morning) "
            "+ P(Hole|Evening)P(Evening)"
        )
        result["answer"] = f"{p_hole:.4f} = {p_hole * 100:.2f}%"
        result["steps"] = [
            f"P(Morning) = {p_morning:.4f}",
            f"P(Evening) = {p_evening:.4f}",
            f"P(Hole | Morning) = {p_hole_morning:.4f}",
            f"P(Hole | Evening) = {p_hole_evening:.4f}",
            f"Total probability = {p_hole:.4f}"
        ]
        result["labels"] = ["Morning Hole", "Evening Hole"]
        result["values"] = [
            int((morning["Defect_Type"].str.lower() == "hole").sum()),
            int((evening["Defect_Type"].str.lower() == "hole").sum())
        ]
        result["graph_title"] = "Hole records by shift"

    # 13. Complement rule
    elif topic == "complement":
        count = int((df["Defect_Rate"] > 3).sum())
        probability = 1 - count / n

        result["formula"] = "P(not A) = 1 - P(A)"
        result["answer"] = f"{probability:.4f} = {probability * 100:.2f}%"
        result["steps"] = [
            f"Rows with defect rate > 3% = {count}",
            f"Rows with defect rate <= 3% = {n - count}",
            f"P(defect rate <= 3%) = 1 - {count}/{n}",
            f"Answer = {probability:.4f}"
        ]
        result["labels"] = ["Rate <= 3%", "Rate > 3%"]
        result["values"] = [n - count, count]
        result["graph_title"] = "Complement probability"

    # 14. Correlation
    elif topic == "correlation":
        r = df["Temperature"].corr(df["Defect_Rate"])

        result["formula"] = (
            "Pearson correlation r = corr(Temperature, Defect rate)"
        )
        result["answer"] = f"r = {r:.4f}"
        result["steps"] = [
            "Har row ka defect percentage calculate kiya.",
            "Temperature aur defect rate ka Pearson correlation nikala.",
            f"Correlation coefficient r = {r:.4f}",
            "Correlation causation prove nahi karta."
        ]
        result["labels"] = df["Temperature"].round(2).tolist()
        result["values"] = df["Defect_Rate"].round(3).tolist()
        result["graph_title"] = "Temperature vs defect rate"

    else:
        return jsonify({"error": "Unknown topic"}), 404

    return jsonify(result)


if __name__ == "__main__":
    app.run(debug=True)
