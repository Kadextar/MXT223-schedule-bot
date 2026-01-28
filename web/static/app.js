async function loadData() {
  const card = document.querySelector(".card");
  const status = document.getElementById("status");

  card.classList.add("fade");
  status.textContent = "Обновление…";

  try {
    const res = await fetch("/api/week-load");
    const data = await res.json();

    document.getElementById("week").textContent = data.week ?? "—";
    document.getElementById("lectures").textContent = data.lectures ?? "—";
    document.getElementById("seminars").textContent = data.seminars ?? "—";
    document.getElementById("hours").textContent = data.total_hours ?? "—";
    document.getElementById("hardest").textContent = data.hardest_day ?? "—";
    document.getElementById("easiest").textContent = data.easiest_day ?? "—";

    status.textContent = "Обновлено ✓";
  } catch (e) {
    status.textContent = "Ошибка загрузки";
  }

  card.classList.remove("fade");
  card.classList.add("show");
}

document.addEventListener("DOMContentLoaded", () => {
  document.getElementById("refresh").addEventListener("click", loadData);
  loadData(); // автозагрузка при открытии
});
