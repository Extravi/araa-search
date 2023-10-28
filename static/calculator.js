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

const calcInput = document.getElementById('current_calc');
const numberButtons = document.querySelectorAll('.calc-btn-style:not(#ce):not(#backspace)');
const addBtn = document.getElementById('add');
const subtractBtn = document.getElementById('subtract');
const multiplyBtn = document.getElementById('multiply');
const divideBtn = document.getElementById('divide');
const equalsBtn = document.getElementById('equals');
const clearBtn = document.getElementById('ce');
const backspaceBtn = document.getElementById('backspace');

document.body.addEventListener('keydown', (key) => {
  if (key.target.tagName.toLowerCase() == "input") {
    return;
  }

  if ('0123456789().'.includes(key.key)) {
    numberButtonHandle(key.key);
  }
  else if ('+-*/'.includes(key.key)) {
    calcInput.textContent += ` ${key.key}`;
  }
  else switch (key.key) {
    case 'Backspace':
      doBackspace();
      break;
    case 'Enter':
      evaluateExpression();
      break;
  }
})

numberButtons.forEach(button => {
  button.addEventListener('click', () => numberButtonHandle(button.textContent));
});

addBtn.addEventListener('click', () => {
  calcInput.textContent += ' +';
});

subtractBtn.addEventListener('click', () => {
  calcInput.textContent += ' -';
});

multiplyBtn.addEventListener('click', () => {
  calcInput.textContent += ' *';
});

divideBtn.addEventListener('click', () => {
  calcInput.textContent += ' /';
});

clearBtn.addEventListener('click', () => {
  calcInput.textContent = '0';
});

backspaceBtn.addEventListener('click', doBackspace);

equalsBtn.addEventListener('click', evaluateExpression);

// Executes a 'backspace' on the calculator's expression.
// Made to reduce repetitive code.
function doBackspace() {
  do {
    calcInput.textContent = calcInput.textContent.slice(0, -1);
  } while (calcInput.textContent.endsWith(' '));
  // ^^^ Sometimes there are spaces in the expression (see above listeners).
  // Remove them aswell.

  // If the contents of calcInput have been completely cleared, output 0
  // to the textbox to match the clear button's behaviour.
  if (calcInput.textContent.length === 0) {
    calcInput.textContent = '0';
  }
}

// Handles the presses to all numberButtons.
function numberButtonHandle(button) {
  // remove any 0 output.
  if (calcInput.textContent === '0' && button !== ".") {
    calcInput.textContent = "";
  }

  // If the end of calcInput has an operator, append an extra space for
  // the number to make the expression look better.
  if (/\+|\-|\*|\//.test(calcInput.textContent[calcInput.textContent.length - 1])) {
    calcInput.textContent += ' ';
  }

  // If statement will prevent multiple dots.
  if (!(calcInput.textContent.includes('.') && button === '.')) {
    calcInput.textContent += button;
  }
}

// Implementation from https://github.com/TommyPang/SimpleCalculator.
// Slightly modified.

function evaluateExpression() {
  let expression = calcInput.textContent;
  document.querySelector(".prev_calculation").textContent = expression;
  expression = expression.replace(/\s/g, '');
  calcInput.textContent = helper(Array.from(expression));
}

function helper(s, idx = 0) {
  var stk = [];
  let sign = '+';
  let num = 0;
  let decimalFlag = false;
  let decimalDivider = 1;

  for (let i = idx; i < s.length; i++) {
    let c = s[i];

    if (c >= '0' && c <= '9') {
      if (decimalFlag) {
        // Handle numbers after decimal point
        decimalDivider *= 10;
        num = num + (parseInt(c) / decimalDivider);
      } else {
        // Handle whole numbers
        num = num * 10 + (c - '0');
      }
    } else if (c === '.') {
      decimalFlag = true;
    }

    if ((!(c >= '0' && c <= '9') && c !== '.') || i === s.length - 1) {
      if (c === '(') {
        num = helper(s, i + 1);
        let l = 1,
          r = 0;
        for (let j = i + 1; j < s.length; j++) {
          if (s[j] === ')') {
            r++;
            if (r === l) {
              i = j;
              break;
            }
          } else if (s[j] === '(') l++;
        }
      }

      let pre = -1;
      switch (sign) {
        case '+':
          stk.push(num);
          break;
        case '-':
          stk.push(num * -1);
          break;
        case '*':
          pre = stk.pop();
          stk.push(pre * num);
          break;
        case '/':
          pre = stk.pop();
          stk.push(pre / num);
          break;
      }
      sign = c;
      num = 0;
      decimalFlag = false;
      decimalDivider = 1;

      if (c === ')') {
        break;
      }
    }
  }

  let ans = 0;
  while (stk.length > 0) {
    ans += stk.pop();
  }
  return ans;
}
