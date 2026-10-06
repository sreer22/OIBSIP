package com.example.quizapplication;

import android.app.Activity;
import android.content.Intent;
import android.os.Bundle;
import android.widget.Button;

public class MainActivity extends Activity {

    @Override
    protected void onCreate(Bundle savedInstanceState) {
        super.onCreate(savedInstanceState);
        setContentView(R.layout.activity_main);

        Button startButton = findViewById(R.id.buttonStartQuiz);
        startButton.setOnClickListener(view ->
                startActivity(new Intent(this, QuizActivity.class)));
    }
}
