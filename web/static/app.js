async function loadData() {
  const card = document.querySelector(".card");
  card.classList.add("fade");

  const res = await fetch("/api/week-load");
  const data = await res.json();

  setTimeout(() => {
    document.getElementById("week").textContent = data.week;
    document.getElementById("lectures").textContent = data.lectures;
    document.getElementById("seminars").textContent = data.seminars;
    document.getElementById("hours").textContent = data.total_hours;
    document.getElementById("hardest").textContent = data.hardest_day;
    document.getElementById("easiest").textContent = data.easiest_day;

    document.getElementById("status").textContent = "Обновлено ✓";
    card.classList.remove("fade");
    card.classList.add("show");
  }, 200);
}

/* 🔥 ВОТ ЭТО БЫЛО ОТСУТСТВУЮЩЕЕ ЗВЕНО */
document.addEventListener("DOMContentLoaded", () => {
  document.getElementById("refresh").addEventListener("click", loadData);
  loadData(); // автозагрузка при открытии
});
