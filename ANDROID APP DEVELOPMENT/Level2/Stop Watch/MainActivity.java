package com.example.stopwatch;

import android.os.Bundle;
import android.os.Handler;
import android.os.SystemClock;
import android.graphics.Color;
import android.view.View;
import android.widget.Button;
import android.widget.LinearLayout;
import android.widget.TextView;

import androidx.appcompat.app.AppCompatActivity;

public class MainActivity extends AppCompatActivity {

    private TextView tvTimer;
    private Button btnStart, btnPause, btnReset, btnLap;
    private LinearLayout lapContainer;

    private Handler handler = new Handler();

    private long startTime = 0;
    private long elapsedTime = 0;

    private boolean isRunning = false;

    private final Runnable stopwatchRunnable = new Runnable() {
        @Override
        public void run() {

            if (isRunning) {

                elapsedTime = SystemClock.elapsedRealtime() - startTime;

                updateTimer();

                handler.postDelayed(this, 50);
            }
        }
    };

    @Override
    protected void onCreate(Bundle savedInstanceState) {
        super.onCreate(savedInstanceState);

        setContentView(R.layout.activity_main);

        tvTimer = findViewById(R.id.tvTimer);

        btnStart = findViewById(R.id.btnStart);
        btnPause = findViewById(R.id.btnPause);
        btnReset = findViewById(R.id.btnReset);
        btnLap = findViewById(R.id.btnLap);

        lapContainer = findViewById(R.id.lapContainer);

        btnStart.setOnClickListener(v -> startStopwatch());

        btnPause.setOnClickListener(v -> pauseStopwatch());

        btnReset.setOnClickListener(v -> resetStopwatch());

        btnLap.setOnClickListener(v -> recordLap());
    }

    private void startStopwatch() {

        if (!isRunning) {

            startTime = SystemClock.elapsedRealtime() - elapsedTime;

            isRunning = true;

            handler.post(stopwatchRunnable);

            btnStart.setEnabled(false);
            btnPause.setEnabled(true);
            btnLap.setEnabled(true);

            btnStart.setText("RUNNING");
        }
    }

    private void pauseStopwatch() {

        if (isRunning) {

            elapsedTime = SystemClock.elapsedRealtime() - startTime;

            isRunning = false;

            handler.removeCallbacks(stopwatchRunnable);

            updateTimer();

            btnStart.setEnabled(true);
            btnPause.setEnabled(false);
            btnLap.setEnabled(false);

            btnStart.setText("START");
        }
    }

    private void resetStopwatch() {

        isRunning = false;

        handler.removeCallbacks(stopwatchRunnable);

        elapsedTime = 0;
        startTime = 0;

        updateTimer();

        lapContainer.removeAllViews();

        btnStart.setEnabled(true);
        btnPause.setEnabled(false);
        btnLap.setEnabled(false);

        btnStart.setText("START");
    }

    private void updateTimer() {

        long totalSeconds = elapsedTime / 1000;

        long hours = totalSeconds / 3600;

        long minutes = (totalSeconds % 3600) / 60;

        long seconds = totalSeconds % 60;

        long milliseconds = (elapsedTime % 1000) / 10;

        String time = String.format(
                "%02d:%02d:%02d",
                hours,
                minutes,
                seconds
        );

        tvTimer.setText(time);
    }

    private void recordLap() {

        if (!isRunning) {
            return;
        }

        long totalSeconds = elapsedTime / 1000;

        long hours = totalSeconds / 3600;

        long minutes = (totalSeconds % 3600) / 60;

        long seconds = totalSeconds % 60;

        String lapTime = String.format(
                "%02d:%02d:%02d",
                hours,
                minutes,
                seconds
        );

        TextView lapText = new TextView(this);

        int lapNumber = lapContainer.getChildCount() + 1;

        lapText.setText(
                "Lap " + lapNumber + "     " + lapTime
        );

        lapText.setTextSize(18);

        lapText.setTextColor(Color.DKGRAY);

        lapText.setPadding(
                15,
                15,
                15,
                15
        );

        lapContainer.addView(lapText);
    }

    @Override
    protected void onPause() {
        super.onPause();

        /*
         * Do not reset the timer here.
         * The elapsed time is calculated using SystemClock.elapsedRealtime(),
         * so the stopwatch can continue accurately when the Activity returns.
         */
    }

    @Override
    protected void onResume() {
        super.onResume();

        if (isRunning) {

            startTime = SystemClock.elapsedRealtime() - elapsedTime;

            handler.removeCallbacks(stopwatchRunnable);

            handler.post(stopwatchRunnable);
        }
    }

    @Override
    protected void onDestroy() {
        super.onDestroy();

        handler.removeCallbacks(stopwatchRunnable);
    }
}