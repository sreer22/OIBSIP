package com.example.quizapplication;

import android.app.Activity;
import android.content.Intent;
import android.content.res.ColorStateList;
import android.graphics.Color;
import android.os.Bundle;
import android.widget.Button;
import android.widget.RadioButton;
import android.widget.RadioGroup;
import android.widget.TextView;
import android.widget.Toast;

import java.util.ArrayList;
import java.util.Collections;
import java.util.List;

public class QuizActivity extends Activity {

    private static final int COLOR_DEFAULT = Color.rgb(49, 87, 213);
    private static final int COLOR_CORRECT = Color.rgb(33, 122, 60);
    private static final int COLOR_INCORRECT = Color.rgb(180, 35, 24);

    private final List<Question> questions = new ArrayList<>();
    private TextView progressText;
    private TextView questionText;
    private TextView feedbackText;
    private RadioGroup answerGroup;
    private Button nextButton;
    private int questionIndex;
    private int correctCount;
    private boolean answerSubmitted;

    @Override
    protected void onCreate(Bundle savedInstanceState) {
        super.onCreate(savedInstanceState);
        setContentView(R.layout.activity_quiz);

        progressText = findViewById(R.id.textProgress);
        questionText = findViewById(R.id.textQuestion);
        feedbackText = findViewById(R.id.textFeedback);
        answerGroup = findViewById(R.id.answerGroup);
        nextButton = findViewById(R.id.buttonNext);

        loadQuestions();
        Collections.shuffle(questions);

        answerGroup.setOnCheckedChangeListener((group, checkedId) -> {
            if (checkedId != -1 && !answerSubmitted) {
                showAnswerFeedback(checkedId);
            }
        });
        nextButton.setOnClickListener(view -> showNextQuestion());
        showQuestion();
    }

    private void loadQuestions() {
        questions.add(new Question("What is the capital of Japan?",
                "Seoul", "Tokyo", "Beijing", "Bangkok", 1));
        questions.add(new Question("Which planet is known as the Red Planet?",
                "Venus", "Jupiter", "Mars", "Mercury", 2));
        questions.add(new Question("How many sides does a hexagon have?",
                "Five", "Six", "Seven", "Eight", 1));
        questions.add(new Question("Which is the largest ocean on Earth?",
                "Atlantic Ocean", "Indian Ocean", "Arctic Ocean", "Pacific Ocean", 3));
        questions.add(new Question("What is the chemical symbol for gold?",
                "Ag", "Au", "Fe", "Go", 1));
        questions.add(new Question("Who wrote the play Romeo and Juliet?",
                "Charles Dickens", "William Shakespeare", "Jane Austen", "Mark Twain", 1));
        questions.add(new Question("Which gas do plants absorb from the atmosphere?",
                "Oxygen", "Nitrogen", "Carbon dioxide", "Hydrogen", 2));
        questions.add(new Question("What is the largest mammal in the world?",
                "African elephant", "Blue whale", "Giraffe", "Hippopotamus", 1));
        questions.add(new Question("How many continents are there on Earth?",
                "Five", "Six", "Seven", "Eight", 2));
        questions.add(new Question("Which instrument has keys, pedals, and strings?",
                "Violin", "Flute", "Piano", "Drum", 2));
    }

    private void showQuestion() {
        Question question = questions.get(questionIndex);
        progressText.setText(getString(
                R.string.question_progress, questionIndex + 1, questions.size()));
        questionText.setText(question.prompt);
        setOption(R.id.optionOne, question.options[0]);
        setOption(R.id.optionTwo, question.options[1]);
        setOption(R.id.optionThree, question.options[2]);
        setOption(R.id.optionFour, question.options[3]);
        resetOptionColors();
        answerGroup.clearCheck();
        answerSubmitted = false;
        feedbackText.setText("");
        nextButton.setEnabled(false);
        nextButton.setText(questionIndex == questions.size() - 1
                ? R.string.finish_quiz
                : R.string.next_question);
    }

    private void setOption(int viewId, String text) {
        RadioButton option = findViewById(viewId);
        option.setText(text);
        option.setEnabled(true);
    }

    private void showAnswerFeedback(int selectedId) {
        answerSubmitted = true;
        Question question = questions.get(questionIndex);
        int selectedIndex = answerGroup.indexOfChild(findViewById(selectedId));
        int correctId = getOptionId(question.correctOption);

        if (selectedIndex == question.correctOption) {
            correctCount++;
            feedbackText.setText(R.string.correct_feedback);
            feedbackText.setTextColor(COLOR_CORRECT);
        } else {
            feedbackText.setText(R.string.incorrect_feedback);
            feedbackText.setTextColor(COLOR_INCORRECT);
            RadioButton selectedOption = findViewById(selectedId);
            selectedOption.setTextColor(COLOR_INCORRECT);
            selectedOption.setButtonTintList(ColorStateList.valueOf(COLOR_INCORRECT));
        }

        RadioButton correctOption = findViewById(correctId);
        correctOption.setTextColor(COLOR_CORRECT);
        correctOption.setButtonTintList(ColorStateList.valueOf(COLOR_CORRECT));

        for (int i = 0; i < answerGroup.getChildCount(); i++) {
            answerGroup.getChildAt(i).setEnabled(false);
        }
        nextButton.setEnabled(true);
    }

    private int getOptionId(int optionIndex) {
        switch (optionIndex) {
            case 0:
                return R.id.optionOne;
            case 1:
                return R.id.optionTwo;
            case 2:
                return R.id.optionThree;
            case 3:
                return R.id.optionFour;
            default:
                throw new IllegalArgumentException("Option index must be between 0 and 3.");
        }
    }

    private void resetOptionColors() {
        int[] optionIds = {
                R.id.optionOne, R.id.optionTwo, R.id.optionThree, R.id.optionFour
        };
        for (int optionId : optionIds) {
            RadioButton option = findViewById(optionId);
            option.setTextColor(Color.rgb(34, 34, 34));
            option.setButtonTintList(ColorStateList.valueOf(COLOR_DEFAULT));
        }
    }

    private void showNextQuestion() {
        if (!answerSubmitted) {
            Toast.makeText(this, R.string.select_answer, Toast.LENGTH_SHORT).show();
            return;
        }

        questionIndex++;
        if (questionIndex < questions.size()) {
            showQuestion();
            return;
        }

        Intent resultIntent = new Intent(this, ResultActivity.class);
        resultIntent.putExtra(ResultActivity.EXTRA_CORRECT, correctCount);
        resultIntent.putExtra(ResultActivity.EXTRA_TOTAL, questions.size());
        startActivity(resultIntent);
        finish();
    }

    private static final class Question {
        private final String prompt;
        private final String[] options;
        private final int correctOption;

        private Question(
                String prompt,
                String optionOne,
                String optionTwo,
                String optionThree,
                String optionFour,
                int correctOption) {
            this.prompt = prompt;
            this.options = new String[]{optionOne, optionTwo, optionThree, optionFour};
            this.correctOption = correctOption;
        }
    }
}
