package com.example.quizapplication;

import android.app.Activity;
import android.content.Intent;
import android.os.Bundle;
import android.widget.Button;
import android.widget.TextView;

public class ResultActivity extends Activity {

    static final String EXTRA_CORRECT = "com.example.quizapplication.CORRECT";
    static final String EXTRA_TOTAL = "com.example.quizapplication.TOTAL";

    @Override
    protected void onCreate(Bundle savedInstanceState) {
        super.onCreate(savedInstanceState);
        setContentView(R.layout.activity_result);

        int total = getIntent().getIntExtra(EXTRA_TOTAL, 10);
        int correct = getIntent().getIntExtra(EXTRA_CORRECT, 0);
        int incorrect = total - correct;

        TextView scoreText = findViewById(R.id.textScore);
        TextView correctText = findViewById(R.id.textCorrect);
        TextView incorrectText = findViewById(R.id.textIncorrect);
        scoreText.setText(getString(R.string.score_format, correct, total));
        correctText.setText(getString(R.string.correct_format, correct));
        incorrectText.setText(getString(R.string.incorrect_format, incorrect));

        Button restartButton = findViewById(R.id.buttonRestartQuiz);
        restartButton.setOnClickListener(view -> {
            Intent intent = new Intent(this, QuizActivity.class);
            startActivity(intent);
            finish();
        });
    }
}
