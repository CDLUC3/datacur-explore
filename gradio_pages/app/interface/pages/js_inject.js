(function addPrintButton() {
  // 1) Don’t run if we've already inserted the button
  if (document.getElementById("print-readme-button")) return;

  // 2) Find the rendered README Markdown
  const readmeProse = document.querySelector("#readme-markdown .prose");
  if (!readmeProse) {
    // not on the README tab (or it hasn’t rendered yet)
    console.debug("print button: readme container not found – skipping injection");
    return;
  }

  // 3) Create the button
  const btn = document.createElement("button");
  btn.id = "print-readme-button";
  btn.textContent = "🖨️ Print README";
  btn.style.cssText = "margin-top: 10px; padding: 8px; font-size: 14px;";

  btn.onclick = function () {
    const target = readmeProse;
    if (!target) {
      alert("Could not find #readme-markdown .prose");
      return;
    }
    const newWindow = window.open("", "_blank");
    newWindow.document.write(`
      <html><head><title>Printable README</title>
      <style>
        body { font-family: sans-serif; padding: 1in; color: black; background: white; }
        * { box-sizing: border-box; }
      </style>
      </head><body>
        ${target.innerHTML}
      </body></html>
    `);
    newWindow.document.close();
    newWindow.focus();
    newWindow.print();
  };

  // 4) Insert the button *after* the prose
  readmeProse.insertAdjacentElement("afterend", btn);
  console.debug("print button injected");
})();
