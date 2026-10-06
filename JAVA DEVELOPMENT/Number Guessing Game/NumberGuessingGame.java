import java.awt.BorderLayout;
import java.awt.Color;
import java.awt.Dimension;
import java.awt.Font;
import java.awt.GradientPaint;
import java.awt.Graphics;
import java.awt.Graphics2D;
import java.awt.GridBagConstraints;
import java.awt.GridBagLayout;
import java.awt.Insets;
import java.awt.RenderingHints;
import java.util.ArrayList;
import java.util.List;
import java.util.Random;
import javax.swing.BorderFactory;
import javax.swing.JButton;
import javax.swing.JComboBox;
import javax.swing.JFrame;
import javax.swing.JLabel;
import javax.swing.JPanel;
import javax.swing.JScrollPane;
import javax.swing.JTextArea;
import javax.swing.JTextField;
import javax.swing.Timer;
import javax.swing.SwingConstants;
import javax.swing.SwingUtilities;
import javax.swing.WindowConstants;
import javax.swing.border.EmptyBorder;

public class NumberGuessingGame {

    private static final Color BACKGROUND = new Color(245, 247, 251);
    private static final Color NAVY = new Color(30, 41, 59);
    private static final Color MUTED = new Color(100, 116, 139);
    private static final Color BLUE = new Color(55, 94, 230);
    private static final Color GREEN = new Color(22, 128, 77);
    private static final Color RED = new Color(190, 50, 50);
    private static final Random RANDOM = new Random();

    private enum Difficulty {
        EASY("Easy", 1, 50, 10),
        MEDIUM("Medium", 1, 100, 7),
        HARD("Hard", 1, 200, 5);

        private final String label;
        private final int minimum;
        private final int maximum;
        private final int maximumAttempts;

        Difficulty(String label, int minimum, int maximum, int maximumAttempts) {
            this.label = label;
            this.minimum = minimum;
            this.maximum = maximum;
            this.maximumAttempts = maximumAttempts;
        }

        @Override
        public String toString() {
            return label + " (" + minimum + "-" + maximum
                    + ", " + maximumAttempts + " attempts)";
        }
    }

    public static void main(String[] args) {
        SwingUtilities.invokeLater(() -> new GameWindow().setVisible(true));
    }

    private static final class GameWindow {

        private final JFrame frame = new JFrame("Number Guessing Game");
        private final JComboBox<Difficulty> difficultyPicker =
                new JComboBox<>(Difficulty.values());
        private final JTextField guessInput = new JTextField();
        private final JButton guessButton = new JButton("Make a guess");
        private final JButton newRoundButton = new JButton("New round");
        private final JLabel roundLabel = new JLabel();
        private final JLabel rangeLabel = new JLabel();
        private final JLabel attemptsLabel = new JLabel();
        private final JLabel feedbackLabel = new JLabel("Pick a difficulty and make your first guess.");
        private final JTextArea historyArea = new JTextArea();
        private final List<String> roundSummaries = new ArrayList<>();
        private final AttemptMeter attemptMeter = new AttemptMeter();
        private final CelebrationPanel celebrationPanel = new CelebrationPanel();
        private Timer feedbackAnimation;

        private Difficulty difficulty;
        private int answer;
        private int attempts;
        private int roundNumber;
        private int wins;
        private boolean roundFinished;

        private GameWindow() {
            frame.setDefaultCloseOperation(WindowConstants.EXIT_ON_CLOSE);
            frame.setMinimumSize(new Dimension(620, 580));
            frame.setSize(720, 680);
            frame.setLocationRelativeTo(null);
            frame.getContentPane().setBackground(BACKGROUND);
            frame.setLayout(new BorderLayout(18, 18));

            frame.add(buildHeader(), BorderLayout.NORTH);
            frame.add(buildGameCard(), BorderLayout.CENTER);
            frame.add(buildHistoryCard(), BorderLayout.EAST);

            guessButton.addActionListener(event -> submitGuess());
            guessInput.addActionListener(event -> submitGuess());
            newRoundButton.addActionListener(event -> startRound());

            startRound();
        }

        private void setVisible(boolean visible) {
            frame.setVisible(visible);
        }

        private JPanel buildHeader() {
            JPanel header = new JPanel(new BorderLayout());
            header.setBackground(NAVY);
            header.setBorder(new EmptyBorder(22, 28, 22, 28));

            JLabel title = new JLabel("Number Guessing Game");
            title.setFont(new Font(Font.SANS_SERIF, Font.BOLD, 25));
            title.setForeground(Color.WHITE);
            header.add(title, BorderLayout.NORTH);

            JLabel subtitle = new JLabel("A little logic, a little luck. Can you find the number?");
            subtitle.setFont(new Font(Font.SANS_SERIF, Font.PLAIN, 14));
            subtitle.setForeground(new Color(203, 213, 225));
            subtitle.setBorder(new EmptyBorder(6, 0, 0, 0));
            header.add(subtitle, BorderLayout.CENTER);
            return header;
        }

        private JPanel buildGameCard() {
            JPanel card = new JPanel(new GridBagLayout());
            card.setBackground(Color.WHITE);
            card.setBorder(BorderFactory.createCompoundBorder(
                    BorderFactory.createLineBorder(new Color(226, 232, 240)),
                    new EmptyBorder(22, 24, 22, 24)));

            GridBagConstraints constraints = new GridBagConstraints();
            constraints.gridx = 0;
            constraints.gridy = 0;
            constraints.gridwidth = 2;
            constraints.weightx = 1;
            constraints.fill = GridBagConstraints.HORIZONTAL;
            constraints.anchor = GridBagConstraints.WEST;
            constraints.insets = new Insets(5, 0, 10, 0);

            roundLabel.setFont(new Font(Font.SANS_SERIF, Font.BOLD, 20));
            roundLabel.setForeground(NAVY);
            card.add(roundLabel, constraints);

            constraints.gridy++;
            rangeLabel.setFont(new Font(Font.SANS_SERIF, Font.PLAIN, 14));
            rangeLabel.setForeground(MUTED);
            card.add(rangeLabel, constraints);

            constraints.gridy++;
            constraints.insets = new Insets(14, 0, 5, 0);
            JLabel difficultyLabel = new JLabel("Difficulty");
            difficultyLabel.setFont(new Font(Font.SANS_SERIF, Font.BOLD, 13));
            difficultyLabel.setForeground(NAVY);
            card.add(difficultyLabel, constraints);

            constraints.gridy++;
            constraints.insets = new Insets(0, 0, 10, 0);
            difficultyPicker.setFont(new Font(Font.SANS_SERIF, Font.PLAIN, 14));
            difficultyPicker.setBackground(Color.WHITE);
            difficultyPicker.setFocusable(false);
            card.add(difficultyPicker, constraints);

            constraints.gridy++;
            attemptsLabel.setFont(new Font(Font.SANS_SERIF, Font.BOLD, 14));
            attemptsLabel.setForeground(BLUE);
            card.add(attemptsLabel, constraints);

            constraints.gridy++;
            constraints.insets = new Insets(0, 0, 6, 0);
            card.add(attemptMeter, constraints);

            constraints.gridy++;
            constraints.insets = new Insets(16, 0, 8, 0);
            guessInput.setFont(new Font(Font.SANS_SERIF, Font.PLAIN, 20));
            guessInput.setHorizontalAlignment(JTextField.CENTER);
            guessInput.setPreferredSize(new Dimension(240, 46));
            guessInput.setBorder(BorderFactory.createCompoundBorder(
                    BorderFactory.createLineBorder(new Color(203, 213, 225)),
                    new EmptyBorder(5, 10, 5, 10)));
            card.add(guessInput, constraints);

            constraints.gridy++;
            constraints.insets = new Insets(6, 0, 12, 0);
            stylePrimaryButton(guessButton);
            card.add(guessButton, constraints);

            constraints.gridy++;
            constraints.insets = new Insets(8, 0, 8, 0);
            feedbackLabel.setFont(new Font(Font.SANS_SERIF, Font.BOLD, 15));
            feedbackLabel.setForeground(MUTED);
            feedbackLabel.setHorizontalAlignment(SwingConstants.CENTER);
            card.add(feedbackLabel, constraints);

            constraints.gridy++;
            constraints.insets = new Insets(0, 0, 0, 0);
            card.add(celebrationPanel, constraints);

            constraints.gridy++;
            constraints.insets = new Insets(12, 0, 0, 0);
            styleSecondaryButton(newRoundButton);
            card.add(newRoundButton, constraints);
            return card;
        }

        private JPanel buildHistoryCard() {
            JPanel card = new JPanel(new BorderLayout(0, 12));
            card.setPreferredSize(new Dimension(220, 0));
            card.setBackground(Color.WHITE);
            card.setBorder(BorderFactory.createCompoundBorder(
                    BorderFactory.createLineBorder(new Color(226, 232, 240)),
                    new EmptyBorder(18, 16, 18, 16)));

            JLabel title = new JLabel("Round history");
            title.setFont(new Font(Font.SANS_SERIF, Font.BOLD, 17));
            title.setForeground(NAVY);
            card.add(title, BorderLayout.NORTH);

            historyArea.setEditable(false);
            historyArea.setFocusable(false);
            historyArea.setLineWrap(true);
            historyArea.setWrapStyleWord(true);
            historyArea.setFont(new Font(Font.SANS_SERIF, Font.PLAIN, 13));
            historyArea.setForeground(new Color(51, 65, 85));
            historyArea.setBackground(Color.WHITE);

            JScrollPane scrollPane = new JScrollPane(historyArea);
            scrollPane.setBorder(BorderFactory.createEmptyBorder());
            scrollPane.getViewport().setBackground(Color.WHITE);
            card.add(scrollPane, BorderLayout.CENTER);
            return card;
        }

        private void startRound() {
            difficulty = (Difficulty) difficultyPicker.getSelectedItem();
            if (difficulty == null) {
                return;
            }

            roundNumber++;
            answer = RANDOM.nextInt(difficulty.maximum - difficulty.minimum + 1)
                    + difficulty.minimum;
            attempts = 0;
            roundFinished = false;
            celebrationPanel.clear();

            roundLabel.setText("Round " + roundNumber);
            rangeLabel.setText("Guess a number from " + difficulty.minimum
                    + " to " + difficulty.maximum + ".");
            guessInput.setText("");
            guessInput.setEnabled(true);
            guessButton.setEnabled(true);
            newRoundButton.setText("New round");
            feedbackLabel.setForeground(MUTED);
            feedbackLabel.setText("You have " + difficulty.maximumAttempts + " attempts. Good luck!");
            feedbackLabel.setFont(new Font(Font.SANS_SERIF, Font.BOLD, 15));
            updateAttemptsLabel();
            guessInput.requestFocusInWindow();
        }

        private void submitGuess() {
            if (roundFinished) {
                return;
            }

            String input = guessInput.getText().trim();
            final int guess;
            try {
                guess = Integer.parseInt(input);
            } catch (NumberFormatException exception) {
                showFeedback("Enter a whole number to make your guess.", RED);
                guessInput.requestFocusInWindow();
                guessInput.selectAll();
                return;
            }

            if (guess < difficulty.minimum || guess > difficulty.maximum) {
                showFeedback("Choose a number from " + difficulty.minimum
                        + " to " + difficulty.maximum + ".", RED);
                guessInput.requestFocusInWindow();
                guessInput.selectAll();
                return;
            }

            attempts++;
            updateAttemptsLabel();
            guessInput.setText("");

            if (guess == answer) {
                finishRound(true, "Correct! You found it in " + attempts
                        + (attempts == 1 ? " attempt." : " attempts.") , GREEN);
            } else if (attempts == difficulty.maximumAttempts) {
                finishRound(false, "You Lost! The number was " + answer + ".", RED);
            } else if (guess < answer) {
                showFeedback("Too Low! Try a higher number.", BLUE);
            } else {
                showFeedback("Too High! Try a lower number.", BLUE);
            }
            guessInput.requestFocusInWindow();
        }

        private void finishRound(boolean won, String message, Color color) {
            roundFinished = true;
            wins += won ? 1 : 0;
            guessInput.setEnabled(false);
            guessButton.setEnabled(false);
            newRoundButton.setText("Play again");
            showFeedback(message, color);
            celebrationPanel.burst(won);

            String summary = won
                    ? "Round " + roundNumber + " - guessed in " + attempts
                            + (attempts == 1 ? " attempt" : " attempts")
                    : "Round " + roundNumber + " - lost after " + attempts
                            + (attempts == 1 ? " attempt" : " attempts")
                            + " (number: " + answer + ")";
            roundSummaries.add(summary);
            historyArea.setText(String.join("\n\n", roundSummaries)
                    + "\n\nScore: " + wins + " of " + roundNumber + " rounds won");
            historyArea.setCaretPosition(historyArea.getDocument().getLength());
        }

        private void updateAttemptsLabel() {
            attemptsLabel.setText("Attempts: " + attempts + " / " + difficulty.maximumAttempts);
            attemptMeter.animateTo((double) attempts / difficulty.maximumAttempts);
        }

        private void showFeedback(String message, Color color) {
            feedbackLabel.setText(message);
            feedbackLabel.setForeground(color);
            feedbackLabel.setFont(new Font(Font.SANS_SERIF, Font.BOLD, 15));

            if (feedbackAnimation != null && feedbackAnimation.isRunning()) {
                feedbackAnimation.stop();
            }

            final long startedAt = System.currentTimeMillis();
            feedbackAnimation = new Timer(25, event -> {
                double progress = Math.min(1.0, (System.currentTimeMillis() - startedAt) / 240.0);
                double pulse = Math.sin(progress * Math.PI);
                feedbackLabel.setFont(new Font(Font.SANS_SERIF, Font.BOLD,
                        15 + (int) Math.round(pulse * 4)));
                if (progress >= 1.0) {
                    ((Timer) event.getSource()).stop();
                    feedbackLabel.setFont(new Font(Font.SANS_SERIF, Font.BOLD, 15));
                }
            });
            feedbackAnimation.start();
        }

        private void stylePrimaryButton(JButton button) {
            button.setFont(new Font(Font.SANS_SERIF, Font.BOLD, 15));
            button.setForeground(Color.WHITE);
            button.setBackground(BLUE);
            button.setFocusPainted(false);
            button.setBorder(new EmptyBorder(12, 18, 12, 18));
            button.setCursor(java.awt.Cursor.getPredefinedCursor(java.awt.Cursor.HAND_CURSOR));
        }

        private void styleSecondaryButton(JButton button) {
            button.setFont(new Font(Font.SANS_SERIF, Font.BOLD, 14));
            button.setForeground(BLUE);
            button.setBackground(new Color(238, 242, 255));
            button.setFocusPainted(false);
            button.setBorder(new EmptyBorder(10, 16, 10, 16));
            button.setCursor(java.awt.Cursor.getPredefinedCursor(java.awt.Cursor.HAND_CURSOR));
        }
    }

    private static final class AttemptMeter extends JPanel {

        private static final long serialVersionUID = 1L;

        private double progress;
        private double targetProgress;
        private final Timer animation;

        private AttemptMeter() {
            setOpaque(false);
            setPreferredSize(new Dimension(260, 16));
            animation = new Timer(16, event -> {
                progress += (targetProgress - progress) * 0.22;
                if (Math.abs(targetProgress - progress) < 0.005) {
                    progress = targetProgress;
                    ((Timer) event.getSource()).stop();
                }
                repaint();
            });
        }

        private void animateTo(double target) {
            targetProgress = Math.max(0, Math.min(1, target));
            animation.start();
        }

        @Override
        protected void paintComponent(Graphics graphics) {
            super.paintComponent(graphics);
            Graphics2D g = (Graphics2D) graphics.create();
            g.setRenderingHint(RenderingHints.KEY_ANTIALIASING, RenderingHints.VALUE_ANTIALIAS_ON);
            int barHeight = 8;
            int y = (getHeight() - barHeight) / 2;
            g.setColor(new Color(232, 237, 246));
            g.fillRoundRect(0, y, getWidth(), barHeight, barHeight, barHeight);
            int fillWidth = (int) Math.round(getWidth() * progress);
            if (fillWidth > 0) {
                g.setPaint(new GradientPaint(0, y, BLUE, Math.max(1, fillWidth), y, GREEN));
                g.fillRoundRect(0, y, fillWidth, barHeight, barHeight, barHeight);
            }
            g.dispose();
        }
    }

    private static final class CelebrationPanel extends JPanel {

        private static final long serialVersionUID = 1L;
        private static final Color[] COLORS = {
                new Color(255, 190, 55),
                new Color(55, 145, 245),
                new Color(75, 190, 125),
                new Color(245, 95, 125),
                new Color(165, 105, 235)
        };

        private transient List<Particle> particles = new ArrayList<>();
        private final Timer animation;

        private CelebrationPanel() {
            setOpaque(false);
            setPreferredSize(new Dimension(280, 40));
            animation = new Timer(25, event -> {
                for (Particle particle : particles) {
                    particle.update();
                }
                particles.removeIf(particle -> particle.life <= 0);
                repaint();
                if (particles.isEmpty()) {
                    ((Timer) event.getSource()).stop();
                }
            });
        }

        private void burst(boolean won) {
            particles.clear();
            Color[] palette = won ? COLORS : new Color[]{RED, new Color(255, 140, 100)};
            int centerX = Math.max(1, getWidth()) / 2;
            int centerY = Math.max(1, getHeight()) / 2;
            for (int i = 0; i < 52; i++) {
                double angle = RANDOM.nextDouble() * Math.PI * 2;
                double speed = 1.2 + RANDOM.nextDouble() * 3.6;
                Color color = palette[RANDOM.nextInt(palette.length)];
                particles.add(new Particle(
                        centerX + RANDOM.nextInt(41) - 20,
                        centerY + RANDOM.nextInt(9) - 4,
                        Math.cos(angle) * speed,
                        Math.sin(angle) * speed - 1.2,
                        color));
            }
            animation.start();
        }

        private void clear() {
            animation.stop();
            particles.clear();
            repaint();
        }

        @Override
        protected void paintComponent(Graphics graphics) {
            super.paintComponent(graphics);
            Graphics2D g = (Graphics2D) graphics.create();
            g.setRenderingHint(RenderingHints.KEY_ANTIALIASING, RenderingHints.VALUE_ANTIALIAS_ON);
            for (Particle particle : particles) {
                g.setColor(new Color(
                        particle.color.getRed(),
                        particle.color.getGreen(),
                        particle.color.getBlue(),
                        Math.min(255, particle.life * 4)));
                if (particle.square) {
                    g.fillRoundRect((int) particle.x, (int) particle.y, 7, 5, 2, 2);
                } else {
                    g.fillOval((int) particle.x, (int) particle.y, 6, 6);
                }
            }
            g.dispose();
        }
    }

    private static final class Particle {
        private double x;
        private double y;
        private final double velocityX;
        private double velocityY;
        private final Color color;
        private final boolean square = RANDOM.nextBoolean();
        private int life = 65;

        private Particle(double x, double y, double velocityX, double velocityY, Color color) {
            this.x = x;
            this.y = y;
            this.velocityX = velocityX;
            this.velocityY = velocityY;
            this.color = color;
        }

        private void update() {
            x += velocityX;
            y += velocityY;
            velocityY += 0.11;
            life--;
        }
    }
}
