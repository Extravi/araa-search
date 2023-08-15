/**
 * @source: ./calculator.js
 * 
 * @licstart  The following is the entire license notice for the
 *  JavaScript code in this page.
 * 
 * Copyright (C) 2023  Extravi
 * 
 * The JavaScript code in this page is free software: you can
 * redistribute it and/or modify it under the terms of the GNU Affero
 * General Public License as published by the Free Software Foundation,
 * either version 3 of the License, or (at your option) any later version.
 * 
 * The code is distributed WITHOUT ANY WARRANTY; without even the
 * implied warranty of MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.
 * See the GNU Affero General Public License for more details.
 * 
 * As additional permission under GNU Affero General Public License
 * section 7, you may distribute non-source (e.g., minimized or compacted)
 * forms of that code without the copy of the GNU Affero General Public
 * License normally required by section 4, provided you include this
 * license notice and a URL through which recipients can access the
 * Corresponding Source.
 * 
 * @licend  The above is the entire license notice
 *  for the JavaScript code in this page.
 */

const calcInput = document.getElementById('calc-input');
const numberButtons = document.querySelectorAll('.calc-btn-style:not(#ce):not(#backspace)');
const addBtn = document.getElementById('add');
const subtractBtn = document.getElementById('subtract');
const multiplyBtn = document.getElementById('multiply');
const divideBtn = document.getElementById('divide');
const equalsBtn = document.getElementById('equals');
const clearBtn = document.getElementById('ce');
const backspaceBtn = document.getElementById('backspace');

numberButtons.forEach(button => {
  button.addEventListener('click', () => {
    // remove any 0 output.
    if (calcInput.textContent === "0") {
      calcInput.textContent = "";
    }

    calcInput.textContent += button.textContent;
  });
});

addBtn.addEventListener('click', () => {
  calcInput.textContent += ' + ';
});

subtractBtn.addEventListener('click', () => {
  calcInput.textContent += ' - ';
});

multiplyBtn.addEventListener('click', () => {
  calcInput.textContent += ' * ';
});

divideBtn.addEventListener('click', () => {
  calcInput.textContent += ' / ';
});

clearBtn.addEventListener('click', () => {
  calcInput.textContent = '';
});

backspaceBtn.addEventListener('click', () => {
  calcInput.textContent = calcInput.textContent.slice(0, -1);
});

equalsBtn.addEventListener('click', () => {
  const expression = calcInput.textContent;
  const result = evaluateExpression(expression);
  calcInput.textContent = result;
});

function evaluateExpression(expression) {
  const parts = expression.split(' ');

  const numbers = [];
  const operators = [];
  for (const part of parts) {
    if (parseFloat(part)) {
      numbers.push(parseFloat(part));
    } else if (part.trim() !== '') {
      operators.push(part);
    }
  }

  // assert(numbers.length === operators.length + 1)
  // TODO: This _may_ change with the addition of parenthesis.
  if (numbers.length !== operators.length + 1) {
    return "Err; not a valid expression!";
  }

  // DM in PEDMAS
  for (let i = 0; i < operators.length; i++) {
    const operator = operators[i];

    // pass if not dividing or multiplying.
    if (operator !== '*' && operator !== '/') {
      continue;
    }

    const nextNumber = numbers[i + 1];
    switch (operator) {
      case '*':
        numbers[i] *= nextNumber;
        break;
      case '/':
        numbers[i] /= nextNumber;
        break;
    }
  }

  // Add and subtract to calculate the final number.
  let total = numbers[0];
  for (let i = 0; i < operators.length; i++) {
    const operator = operators[i];

    // pass if not adding or subtracting.
    if (operator !== '+' && operator !== '-') {
      continue;
    }

    const nextNumber = numbers[i + 1];
    switch (operator) {
      case '+':
        total += nextNumber;
        break;
      case '-':
        total -= nextNumber;
        break;
    }
  }

  return total;
}
