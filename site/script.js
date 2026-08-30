"use strict";

document.documentElement.classList.add("js");

const activateTab = (tabs, panels, nextTab) => {
  tabs.forEach((tab) => {
    const isSelected = tab === nextTab;
    tab.setAttribute("aria-selected", String(isSelected));
    tab.tabIndex = isSelected ? 0 : -1;
    tab.classList.toggle("is-active", isSelected);
  });

  panels.forEach((panel) => {
    panel.hidden = panel.id !== nextTab.getAttribute("aria-controls");
  });
};

const addTabBehavior = (tablist, onChange) => {
  const tabs = Array.from(tablist.querySelectorAll('[role="tab"]'));

  tabs.forEach((tab) => {
    tab.addEventListener("click", () => onChange(tabs, tab));

    tab.addEventListener("keydown", (event) => {
      const currentIndex = tabs.indexOf(tab);
      let nextIndex;

      if (event.key === "ArrowRight" || event.key === "ArrowDown") {
        nextIndex = (currentIndex + 1) % tabs.length;
      } else if (event.key === "ArrowLeft" || event.key === "ArrowUp") {
        nextIndex = (currentIndex - 1 + tabs.length) % tabs.length;
      } else if (event.key === "Home") {
        nextIndex = 0;
      } else if (event.key === "End") {
        nextIndex = tabs.length - 1;
      } else {
        return;
      }

      event.preventDefault();
      onChange(tabs, tabs[nextIndex]);
      tabs[nextIndex].focus();
    });
  });
};

const methodTablist = document.querySelector(".method-tablist");
if (methodTablist) {
  const methodPanels = Array.from(document.querySelectorAll(".method-detail [role='tabpanel']"));
  addTabBehavior(methodTablist, (tabs, nextTab) => activateTab(tabs, methodPanels, nextTab));
}

const resultTablist = document.querySelector(".segmented-control");
if (resultTablist) {
  const resultPanels = Array.from(document.querySelectorAll(".result-panel"));
  const viewDescription = document.querySelector("#result-view-description");
  const descriptions = {
    "result-tab-published": "Original published result files",
    "result-tab-common": "Aligned comparison across the same 193 tasks",
  };

  addTabBehavior(resultTablist, (tabs, nextTab) => {
    activateTab(tabs, resultPanels, nextTab);
    if (viewDescription) {
      viewDescription.textContent = descriptions[nextTab.id];
    }
  });
}

const revealItems = Array.from(document.querySelectorAll(".reveal"));
const reducedMotion = window.matchMedia("(prefers-reduced-motion: reduce)").matches;

if (reducedMotion || !("IntersectionObserver" in window)) {
  revealItems.forEach((item) => item.classList.add("is-visible"));
} else {
  const observer = new IntersectionObserver(
    (entries, revealObserver) => {
      entries.forEach((entry) => {
        if (entry.isIntersecting) {
          entry.target.classList.add("is-visible");
          revealObserver.unobserve(entry.target);
        }
      });
    },
    { rootMargin: "0px 0px -8%", threshold: 0.08 },
  );

  revealItems.forEach((item) => observer.observe(item));
}
