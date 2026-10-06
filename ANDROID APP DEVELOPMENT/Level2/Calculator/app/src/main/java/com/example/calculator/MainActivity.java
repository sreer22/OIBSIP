package com.example.calculator;

import android.app.Activity;
import android.os.Bundle;
import android.widget.TextView;

import java.util.Locale;

public class MainActivity extends Activity {

    private final StringBuilder expression = new StringBuilder();
    private TextView expressionDisplay;
    private TextView resultDisplay;
    private boolean resultShown;
    private boolean hasError;

    @Override
    protected void onCreate(Bundle savedInstanceState) {
        super.onCreate(savedInstanceState);
        setContentView(R.layout.activity_main);

        expressionDisplay = findViewById(R.id.displayExpression);
        resultDisplay = findViewById(R.id.displayResult);

        bindDigit(R.id.buttonZero, "0");
        bindDigit(R.id.buttonOne, "1");
        bindDigit(R.id.buttonTwo, "2");
        bindDigit(R.id.buttonThree, "3");
        bindDigit(R.id.buttonFour, "4");
        bindDigit(R.id.buttonFive, "5");
        bindDigit(R.id.buttonSix, "6");
        bindDigit(R.id.buttonSeven, "7");
        bindDigit(R.id.buttonEight, "8");
        bindDigit(R.id.buttonNine, "9");

        bindOperator(R.id.buttonAdd, "+");
        bindOperator(R.id.buttonSubtract, "-");
        bindOperator(R.id.buttonMultiply, "×");
        bindOperator(R.id.buttonDivide, "÷");

        findViewById(R.id.buttonDecimal).setOnClickListener(view -> appendDecimal());
        findViewById(R.id.buttonClear).setOnClickListener(view -> clear());
        findViewById(R.id.buttonBackspace).setOnClickListener(view -> backspace());
        findViewById(R.id.buttonEquals).setOnClickListener(view -> evaluate());
    }

    private void bindDigit(int buttonId, String digit) {
        findViewById(buttonId).setOnClickListener(view -> appendDigit(digit));
    }

    private void bindOperator(int buttonId, String operator) {
        findViewById(buttonId).setOnClickListener(view -> appendOperator(operator));
    }

    private void appendDigit(String digit) {
        if (hasError || resultShown) {
            expression.setLength(0);
            expressionDisplay.setText("");
            resultShown = false;
            hasError = false;
        }

        expression.append(digit);
        renderExpression();
    }

    private void appendDecimal() {
        if (hasError || resultShown) {
            expression.setLength(0);
            expressionDisplay.setText("");
            resultShown = false;
            hasError = false;
        }

        if (expression.length() == 0 || isOperator(lastCharacter())) {
            expression.append("0.");
        } else {
            int currentNumberStart = findCurrentNumberStart();
            if (expression.indexOf(".", currentNumberStart) == -1) {
                expression.append('.');
            }
        }
        renderExpression();
    }

    private int findCurrentNumberStart() {
        for (int index = expression.length() - 1; index >= 0; index--) {
            if (isOperator(expression.charAt(index))) {
                if (expression.charAt(index) == '-'
                        && (index == 0 || isOperator(expression.charAt(index - 1)))) {
                    continue;
                }
                return index + 1;
            }
        }
        return 0;
    }

    private void appendOperator(String operator) {
        if (hasError) {
            return;
        }
        if (resultShown) {
            resultShown = false;
        }

        if (expression.length() == 0) {
            if ("-".equals(operator)) {
                expression.append(operator);
                renderExpression();
            }
            return;
        }

        char last = lastCharacter();
        if (isOperator(last)) {
            if ("-".equals(operator) && last != '-') {
                expression.append(operator);
            } else if (last == '-' && expression.length() > 1
                    && isOperator(expression.charAt(expression.length() - 2))) {
                expression.setLength(expression.length() - 2);
                expression.append(operator);
            } else {
                expression.setCharAt(expression.length() - 1, operator.charAt(0));
            }
        } else {
            expression.append(operator);
        }
        renderExpression();
    }

    private void backspace() {
        if (hasError || resultShown) {
            clear();
            return;
        }
        if (expression.length() > 0) {
            expression.deleteCharAt(expression.length() - 1);
        }
        renderExpression();
    }

    private void clear() {
        expression.setLength(0);
        expressionDisplay.setText("");
        resultDisplay.setText("0");
        resultShown = false;
        hasError = false;
    }

    private void evaluate() {
        if (expression.length() == 0 || hasError) {
            return;
        }

        String enteredExpression = expression.toString();
        try {
            double result = new ExpressionParser(enteredExpression).parse();
            if (Double.isNaN(result) || Double.isInfinite(result)) {
                showError(enteredExpression);
                return;
            }

            String formattedResult = formatResult(result);
            expressionDisplay.setText(enteredExpression);
            resultDisplay.setText(formattedResult);
            expression.setLength(0);
            expression.append(formattedResult);
            resultShown = true;
        } catch (IllegalArgumentException exception) {
            showError(enteredExpression);
        }
    }

    private void showError(String enteredExpression) {
        expressionDisplay.setText(enteredExpression);
        resultDisplay.setText("Error");
        expression.setLength(0);
        resultShown = false;
        hasError = true;
    }

    private String formatResult(double result) {
        if (result == 0) {
            return "0";
        }
        if (result == Math.rint(result)
                && Math.abs(result) <= Long.MAX_VALUE) {
            return String.format(Locale.US, "%.0f", result);
        }
        return String.format(Locale.US, "%.10f", result)
                .replaceAll("0+$", "")
                .replaceAll("\\.$", "");
    }

    private void renderExpression() {
        expressionDisplay.setText("");
        resultDisplay.setText(expression.length() == 0 ? "0" : expression.toString());
    }

    private char lastCharacter() {
        return expression.charAt(expression.length() - 1);
    }

    private boolean isOperator(char character) {
        return character == '+' || character == '-' || character == '×' || character == '÷';
    }

    private static final class ExpressionParser {
        private final String input;
        private int position;

        private ExpressionParser(String input) {
            this.input = input;
        }

        private double parse() {
            double value = parseExpression();
            skipWhitespace();
            if (position != input.length()) {
                throw new IllegalArgumentException("Unexpected input.");
            }
            return value;
        }

        private double parseExpression() {
            double value = parseTerm();
            while (true) {
                if (consume('+')) {
                    value += parseTerm();
                } else if (consume('-')) {
                    value -= parseTerm();
                } else {
                    return value;
                }
            }
        }

        private double parseTerm() {
            double value = parseUnary();
            while (true) {
                if (consume('×')) {
                    value *= parseUnary();
                } else if (consume('÷')) {
                    double divisor = parseUnary();
                    if (divisor == 0.0) {
                        throw new IllegalArgumentException("Division by zero.");
                    }
                    value /= divisor;
                } else {
                    return value;
                }
            }
        }

        private double parseUnary() {
            if (consume('+')) {
                return parseUnary();
            }
            if (consume('-')) {
                return -parseUnary();
            }
            return parseNumber();
        }

        private double parseNumber() {
            skipWhitespace();
            int start = position;
            boolean hasDigit = false;
            boolean hasDecimal = false;

            while (position < input.length()) {
                char character = input.charAt(position);
                if (character >= '0' && character <= '9') {
                    hasDigit = true;
                    position++;
                } else if (character == '.' && !hasDecimal) {
                    hasDecimal = true;
                    position++;
                } else {
                    break;
                }
            }

            if (!hasDigit) {
                throw new IllegalArgumentException("Expected a number.");
            }
            return Double.parseDouble(input.substring(start, position));
        }

        private boolean consume(char expected) {
            skipWhitespace();
            if (position < input.length() && input.charAt(position) == expected) {
                position++;
                return true;
            }
            return false;
        }

        private void skipWhitespace() {
            while (position < input.length()
                    && Character.isWhitespace(input.charAt(position))) {
                position++;
            }
        }
    }
}
