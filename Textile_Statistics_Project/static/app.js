
const buttons = document.querySelectorAll(".nav");

const pageTitle = document.getElementById("page-title");
const resultTitle = document.getElementById("result-title");
const subtitle = document.getElementById("subtitle");
const dataSection = document.getElementById("data-section");
const calculationSection = document.getElementById("calculation-section");

const formulaBox = document.getElementById("formula");
const answerBox = document.getElementById("answer");
const stepsBox = document.getElementById("steps");
const noteBox = document.getElementById("note");
const chartBox = document.getElementById("chart");

const titles = {
    data: "Textile Data Overview",
    mean: "Mean",
    median: "Median",
    mode: "Mode",
    variance: "Variance",
    sd: "Standard Deviation",
    defect_rate: "Overall Defect Rate",
    machine: "Machine Analysis",
    shift: "Shift Analysis",
    fabric: "Fabric Type Analysis",
    defect_type: "Defect Type Analysis",
    prob_gt3: "Probability: Defect Rate > 3%",
    bayes: "Bayes' Theorem",
    conditional: "Conditional Probability",
    total_probability: "Total Probability Theorem",
    complement: "Complement Rule",
    correlation: "Temperature Correlation"
};

buttons.forEach(button => {
    button.addEventListener("click", () => {
        loadTopic(button.dataset.topic);
    });
});

async function loadTopic(topic) {
    buttons.forEach(button => {
        button.classList.toggle(
            "active",
            button.dataset.topic === topic
        );
    });

    pageTitle.textContent = titles[topic] || "Textile Statistics";
    resultTitle.textContent = titles[topic] || "Calculation";

    if (topic === "data") {
        dataSection.classList.remove("hidden");
        calculationSection.classList.add("hidden");

        subtitle.textContent = "Your original textile dataset";
        return;
    }

    dataSection.classList.add("hidden");
    calculationSection.classList.remove("hidden");

    subtitle.textContent =
        "Formula, step-by-step calculation and graph";

    formulaBox.textContent = "Calculating...";
    answerBox.textContent = "Please wait...";
    stepsBox.innerHTML = "";
    noteBox.textContent = "";
    noteBox.classList.add("hidden");
    chartBox.innerHTML = "";

    try {
        const response = await fetch(
            `/api/calculate/${encodeURIComponent(topic)}`
        );

        const result = await response.json();

        if (!response.ok) {
            throw new Error(result.error || "Calculation failed");
        }

        // Show formula and final answer
        formulaBox.textContent = result.formula;
        answerBox.textContent = result.answer;

        // Show each calculation step
        result.steps.forEach(step => {
            const li = document.createElement("li");
            li.textContent = step;
            stepsBox.appendChild(li);
        });

        // Show notes when necessary
        if (result.note) {
            noteBox.textContent = result.note;
            noteBox.classList.remove("hidden");
        }

        // Draw the graph
        drawGraph(topic, result);

    } catch (error) {
        formulaBox.textContent = "Unable to calculate";
        answerBox.textContent = "Error";
        const li = document.createElement("li");
        li.textContent = error.message;
        stepsBox.appendChild(li);
    }
}

function drawGraph(topic, result) {
    if (!result.labels || result.labels.length === 0) {
        chartBox.innerHTML =
            "<p>No graph is available for this result.</p>";
        return;
    }

    let trace;

    // Scatter plot for correlation
    if (topic === "correlation") {
        trace = {
            x: result.labels,
            y: result.values,
            type: "scatter",
            mode: "markers",
            name: "Observations",
            marker: {
                size: 10
            },
            hovertemplate:
                "Temperature: %{x}<br>" +
                "Defect rate: %{y:.3f}%<extra></extra>"
        };
    } else {
        trace = {
            x: result.labels,
            y: result.values,
            type: "bar",
            name: "Calculated values",
            marker: {
                color: "#3478b9"
            },
            hovertemplate:
                "%{x}<br>Value: %{y}<extra></extra>"
        };
    }

    const layout = {
        title: {
            text: result.graph_title || result.title,
            x: 0.03,
            font: {
                size: 16
            }
        },
        paper_bgcolor: "#ffffff",
        plot_bgcolor: "#ffffff",
        margin: {
            l: 60,
            r: 20,
            t: 65,
            b: 90
        },
        xaxis: {
            title: topic === "correlation"
                ? "Temperature (°C)"
                : "Category / Observation",
            automargin: true,
            tickangle: -25
        },
        yaxis: {
            title: topic === "correlation"
                ? "Defect rate (%)"
                : "Value",
            rangemode: "tozero",
            gridcolor: "#e9eef5"
        },
        showlegend: false
    };

    Plotly.newPlot(
        chartBox,
        [trace],
        layout,
        {
            responsive: true,
            displaylogo: false
        }
    );
}
