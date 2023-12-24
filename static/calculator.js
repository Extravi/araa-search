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
    operatorButtonHandle(key.key);
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

addBtn.addEventListener('click', () => operatorButtonHandle('+'));
subtractBtn.addEventListener('click', () => operatorButtonHandle('-'));
multiplyBtn.addEventListener('click', () => operatorButtonHandle('*'));
divideBtn.addEventListener('click', () => operatorButtonHandle('/'));

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

// Handles the presses to all operator buttons.
function operatorButtonHandle(operator) {
  // Avoid multiple operators being added.
  // This will override the current operator with the new operator being added.
  if (/\+|\-|\*|\//.test(calcInput.textContent.split(' ').pop())) {
    calcInput.textContent = calcInput.textContent.substring(0, calcInput.textContent.length - 1);
  }

  // Make a decimal that's '1234.' into '1234.0' before adding an operator.
  if (calcInput.textContent[calcInput.textContent.length - 1] === '.') {
    calcInput.textContent += '0';
  }

  calcInput.textContent += ` ${operator}`;
}

// Handles the presses to all numberButtons.
function numberButtonHandle(button) {
  // The absolute last char of the expression; i.e. '3' in '4 + 5 * 6 + 2.3'
  const lastChar = calcInput.textContent[calcInput.textContent.length - 1];

  // If the end of calcInput has an operator, append an extra space for
  // the number to make the expression look better.
  if (/\+|\-|\*|\//.test(lastChar)) {
    calcInput.textContent += ' ';
  }
  // Add a multiplication operator around brackets.
  else if ((lastChar === ")" || button === "(") && calcInput.textContent !== '0') {
    operatorButtonHandle('* ');
  }

  // The 'trailing' substring in an expression; i.e. 2.3 in '4 + 5 * 6 + 2.3'
  // Collected here as the expression may have been modified by the above code
  const trailing = calcInput.textContent.split(' ').pop();

  // Do some specific things for decimals.
  if (button === '.') {
    // Prevent multiple dots in a number.
    if (trailing.includes('.')) {
      return;
    }

    // Add an extra 0 if the trailing substring is blank or opening parenthesis
    // Makes thinks look nicer (0.3 instead of .3).
    if (trailing.length === 0 || trailing === '(') {
      calcInput.textContent += '0';
    }
  }
  // Remove any 0 output if a dot is not being added.
  // i.e if 9 is input and the expression is '9 + 0', it'll change
  // to '9 + 9' because of this if statement.
  else if (trailing === '0') {
    calcInput.textContent = calcInput.textContent.substring(0, calcInput.textContent.length - 1);
  }

  calcInput.textContent += button;
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
