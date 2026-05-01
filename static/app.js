document.addEventListener("DOMContentLoaded", function () {
  // Chart Logic (only run if chart exists on page)
  const expenseChartCtx = document.getElementById("expenseChart");
  if (expenseChartCtx) {
    fetch("/chart-data")
      .then((response) => response.json())
      .then((data) => {
        if (data.labels.length === 0) {
          // Replace canvas with "No Data" message
          const container = expenseChartCtx.parentElement;
          container.innerHTML =
            "<div style='display: flex; align-items: center; justify-content: center; height: 100%; color: var(--text-muted);'>No data available for this cycle</div>";
          return;
        }

        const backgroundColors = [
          "#6366f1",
          "#8b5cf6",
          "#ec4899",
          "#10b981",
          "#f59e0b",
          "#3b82f6",
        ];

        new Chart(expenseChartCtx, {
          type: "doughnut",
          data: {
            labels: data.labels,
            datasets: [
              {
                data: data.values,
                backgroundColor: backgroundColors,
                borderWidth: 0,
                hoverOffset: 10,
              },
            ],
          },
          options: {
            responsive: true,
            maintainAspectRatio: false,
            cutout: "75%",
            plugins: {
              legend: {
                position: "bottom",
                labels: {
                  usePointStyle: true,
                  padding: 20,
                  font: {
                    family: "'Inter', sans-serif",
                    size: 12,
                  },
                },
              },
              tooltip: {
                backgroundColor: "rgba(30, 41, 59, 0.9)",
                titleFont: { family: "'Inter', sans-serif" },
                bodyFont: { family: "'Inter', sans-serif" },
                padding: 12,
                cornerRadius: 8,
                callbacks: {
                  label: function (context) {
                    return ` ${context.label}: ${context.raw}%`;
                  },
                },
              },
            },
          },
        });
      })
      .catch((error) => console.error("Error fetching chart data:", error));
  }

  // Setup Budget Form Logic
  const setupForm = document.getElementById("setup-form");
  if (setupForm) {
    const today = new Date().toISOString().split("T")[0];
    document.getElementById("start_date").value = today;

    const amountInput = document.getElementById("amount");
    const startInput = document.getElementById("start_date");
    const endInput = document.getElementById("end_date");
    const summaryBox = document.getElementById("summary");

    function updateSummary() {
      const amount = parseFloat(amountInput.value);
      const startVal = startInput.value;
      const endVal = endInput.value;

      if (!amount || !startVal || !endVal) {
        summaryBox.style.display = "none";
        return;
      }

      const start = new Date(startVal);
      const end = new Date(endVal);
      const days = Math.round((end - start) / (1000 * 60 * 60 * 24));

      if (days <= 0) {
        summaryBox.style.display = "none";
        return;
      }

      document.getElementById("s-amount").textContent = amount.toLocaleString();
      document.getElementById("s-days").textContent = days;
      document.getElementById("s-daily").textContent = (amount / days).toFixed(2);
      summaryBox.style.display = "block";
    }

    amountInput.addEventListener("input", updateSummary);
    startInput.addEventListener("change", updateSummary);
    endInput.addEventListener("change", updateSummary);
  }
});
