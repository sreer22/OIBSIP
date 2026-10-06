import java.awt.BorderLayout;
import java.awt.CardLayout;
import java.awt.Color;
import java.awt.Dimension;
import java.awt.Font;
import java.awt.GridBagConstraints;
import java.awt.GridBagLayout;
import java.awt.Insets;
import java.awt.event.WindowAdapter;
import java.awt.event.WindowEvent;
import java.util.Arrays;
import java.util.concurrent.TimeUnit;
import javax.swing.BorderFactory;
import javax.swing.ButtonGroup;
import javax.swing.JButton;
import javax.swing.JFrame;
import javax.swing.JLabel;
import javax.swing.JOptionPane;
import javax.swing.JPanel;
import javax.swing.JPasswordField;
import javax.swing.JRadioButton;
import javax.swing.JScrollPane;
import javax.swing.JTextField;
import javax.swing.SwingConstants;
import javax.swing.SwingUtilities;
import javax.swing.Timer;
import javax.swing.WindowConstants;
import javax.swing.border.EmptyBorder;

public class OnlineExaminationSystem {

    private static final String LOGIN_CARD = "login";
    private static final String PROFILE_CARD = "profile";
    private static final String EXAM_CARD = "exam";
    private static final String RESULT_CARD = "result";
    private static final int EXAM_DURATION_SECONDS = 60 * 60;

    private static final Color BACKGROUND = new Color(244, 247, 252);
    private static final Color NAVY = new Color(25, 39, 68);
    private static final Color BLUE = new Color(53, 96, 216);
    private static final Color MUTED = new Color(99, 112, 134);
    private static final Color RED = new Color(183, 49, 49);

    private static final Question[] QUESTIONS = {
            new Question("Which keyword is used to inherit a class in Java?",
                    "implements", "extends", "inherits", "instanceof", 1),
            new Question("Which collection does not allow duplicate elements?",
                    "ArrayList", "LinkedList", "HashSet", "Vector", 2),
            new Question("What is the default value of a boolean field in Java?",
                    "true", "false", "null", "0", 1),
            new Question("Which method is the entry point of a standard Java application?",
                    "start()", "run()", "main()", "init()", 2),
            new Question("Which component groups radio buttons in Swing?",
                    "JPanel", "ButtonGroup", "JRadioGroup", "JFrame", 1),
            new Question("What does JVM stand for?",
                    "Java Variable Method", "Java Virtual Machine",
                    "Joined Version Manager", "Java Visual Model", 1),
            new Question("Which keyword prevents a method from being overridden?",
                    "static", "private", "final", "volatile", 2),
            new Question("Which interface is commonly used to sort objects?",
                    "Runnable", "Comparable", "Serializable", "Cloneable", 1),
            new Question("Which Swing class provides a single-line text input?",
                    "JTextArea", "JLabel", "JTextField", "JList", 2),
            new Question("Which block is used to handle an exception?",
                    "try-catch", "if-else", "switch-case", "for-each", 0)
    };

    private final JFrame frame = new JFrame("Online Examination System");
    private final CardLayout cardLayout = new CardLayout();
    private final JPanel cards = new JPanel(cardLayout);

    private final JTextField loginUsername = new JTextField(22);
    private final JPasswordField loginPassword = new JPasswordField(22);
    private final JLabel loginMessage = new JLabel(" ", SwingConstants.CENTER);
    private final JLabel loginDemoHint = new JLabel("", SwingConstants.CENTER);

    private final JTextField profileName = new JTextField(22);
    private final JPasswordField profilePassword = new JPasswordField(22);
    private final JLabel profileMessage = new JLabel(" ", SwingConstants.CENTER);

    private final JLabel examWelcome = new JLabel();
    private final JLabel timerLabel = new JLabel("30:00", SwingConstants.CENTER);
    private final JLabel questionCounter = new JLabel();
    private final JLabel questionPrompt = new JLabel();
    private final JLabel examMessage = new JLabel(" ", SwingConstants.CENTER);
    private final JRadioButton[] options = new JRadioButton[4];
    private final ButtonGroup optionGroup = new ButtonGroup();
    private final JButton previousButton = new JButton("Previous");
    private final JButton nextButton = new JButton("Next");
    private final int[] selectedAnswers = new int[QUESTIONS.length];
    private final Timer countdownTimer;

    private String username = "student";
    private String password = "exam123";
    private String displayName = "Student";
    private int currentQuestion;
    private int remainingSeconds = EXAM_DURATION_SECONDS;
    private int examStartSeconds = EXAM_DURATION_SECONDS;
    private boolean examActive;
    private boolean timeExpired;

    private OnlineExaminationSystem() {
        Arrays.fill(selectedAnswers, -1);
        countdownTimer = new Timer(1000, event -> tickClock());

        frame.setDefaultCloseOperation(WindowConstants.DO_NOTHING_ON_CLOSE);
        frame.setMinimumSize(new Dimension(720, 620));
        frame.setSize(860, 720);
        frame.setLocationRelativeTo(null);
        frame.getContentPane().setBackground(BACKGROUND);
        frame.addWindowListener(new WindowAdapter() {
            @Override
            public void windowClosing(WindowEvent event) {
                confirmWindowClose();
            }
        });

        cards.setBackground(BACKGROUND);
        cards.add(buildLoginCard(), LOGIN_CARD);
        cards.add(buildProfileCard(), PROFILE_CARD);
        cards.add(buildExamCard(), EXAM_CARD);
        cards.add(buildResultCard(), RESULT_CARD);
        frame.setContentPane(cards);
        showLogin();
    }

    public static void main(String[] args) {
        SwingUtilities.invokeLater(() -> new OnlineExaminationSystem().show());
    }

    private void show() {
        frame.setVisible(true);
    }

    private void showLogin() {
        loginUsername.setText(username);
        loginPassword.setText("");
        cardLayout.show(cards, LOGIN_CARD);
    }

    private JPanel buildLoginCard() {
        JPanel page = buildPage();
        page.add(buildHeader("Online Examination", "Sign in to continue to your exam"));

        JPanel form = buildFormCard();
        addField(form, "Username", loginUsername, 0);
        addField(form, "Password", loginPassword, 2);

        JButton loginButton = primaryButton("Login");
        loginButton.addActionListener(event -> login());
        GridBagConstraints constraints = formConstraints(4);
        constraints.insets = new Insets(20, 0, 8, 0);
        form.add(loginButton, constraints);

        loginMessage.setForeground(RED);
        form.add(loginMessage, formConstraints(5));
        loginDemoHint.setForeground(MUTED);
        loginDemoHint.setFont(new Font(Font.SANS_SERIF, Font.PLAIN, 12));
        loginDemoHint.setText("Demo login: student / exam123");
        form.add(loginDemoHint, formConstraints(6));

        page.add(form);
        return page;
    }

    private JPanel buildProfileCard() {
        JPanel page = buildPage();
        page.add(buildHeader("Your Profile", "Confirm your display name and update your password"));

        JPanel form = buildFormCard();
        addField(form, "Display name", profileName, 0);
        addField(form, "New password (leave blank to keep current)", profilePassword, 2);

        JButton beginButton = primaryButton("Save and Start Exam");
        beginButton.addActionListener(event -> saveProfileAndStart());
        GridBagConstraints constraints = formConstraints(4);
        constraints.insets = new Insets(20, 0, 8, 0);
        form.add(beginButton, constraints);

        profileMessage.setForeground(RED);
        form.add(profileMessage, formConstraints(5));
        page.add(form);
        return page;
    }

    private JPanel buildExamCard() {
        JPanel page = buildPage();

        JPanel top = new JPanel(new BorderLayout());
        top.setOpaque(false);
        examWelcome.setFont(new Font(Font.SANS_SERIF, Font.BOLD, 16));
        examWelcome.setForeground(NAVY);
        top.add(examWelcome, BorderLayout.WEST);

        JPanel clockCard = new JPanel(new BorderLayout(4, 0));
        clockCard.setBackground(new Color(232, 238, 252));
        clockCard.setBorder(new EmptyBorder(8, 14, 8, 14));
        JLabel clockCaption = new JLabel("TIME LEFT  ", SwingConstants.CENTER);
        clockCaption.setFont(new Font(Font.SANS_SERIF, Font.BOLD, 10));
        clockCaption.setForeground(MUTED);
        timerLabel.setFont(new Font(Font.MONOSPACED, Font.BOLD, 21));
        timerLabel.setForeground(BLUE);
        clockCard.add(clockCaption, BorderLayout.NORTH);
        clockCard.add(timerLabel, BorderLayout.CENTER);
        top.add(clockCard, BorderLayout.EAST);
        page.add(top);

        JPanel questionCard = buildFormCard();
        questionCounter.setFont(new Font(Font.SANS_SERIF, Font.BOLD, 14));
        questionCounter.setForeground(BLUE);
        questionCard.add(questionCounter, formConstraints(0));

        questionPrompt.setFont(new Font(Font.SANS_SERIF, Font.BOLD, 20));
        questionPrompt.setForeground(NAVY);
        questionPrompt.setBorder(new EmptyBorder(18, 0, 18, 0));
        questionCard.add(questionPrompt, formConstraints(1));

        JPanel optionPanel = new JPanel(new GridBagLayout());
        optionPanel.setOpaque(false);
        for (int index = 0; index < options.length; index++) {
            JRadioButton option = new JRadioButton();
            option.setFont(new Font(Font.SANS_SERIF, Font.PLAIN, 16));
            option.setForeground(new Color(46, 58, 79));
            option.setOpaque(true);
            option.setBackground(Color.WHITE);
            option.setBorder(new EmptyBorder(12, 14, 12, 14));
            option.setFocusPainted(false);
            optionGroup.add(option);
            options[index] = option;
            GridBagConstraints optionConstraints = new GridBagConstraints();
            optionConstraints.gridx = 0;
            optionConstraints.gridy = index;
            optionConstraints.weightx = 1;
            optionConstraints.fill = GridBagConstraints.HORIZONTAL;
            optionConstraints.insets = new Insets(4, 0, 4, 0);
            optionPanel.add(option, optionConstraints);
            option.addActionListener(event -> selectedAnswers[currentQuestion]
                    = findSelectedOption());
        }
        questionCard.add(optionPanel, formConstraints(2));

        examMessage.setFont(new Font(Font.SANS_SERIF, Font.PLAIN, 13));
        examMessage.setForeground(MUTED);
        questionCard.add(examMessage, formConstraints(3));

        JPanel navigation = new JPanel(new BorderLayout(12, 0));
        navigation.setOpaque(false);
        previousButton.addActionListener(event -> navigateQuestion(-1));
        nextButton.addActionListener(event -> navigateQuestion(1));
        navigation.add(previousButton, BorderLayout.WEST);

        JButton submitButton = primaryButton("Submit exam");
        submitButton.addActionListener(event -> confirmSubmit());
        navigation.add(submitButton, BorderLayout.EAST);
        navigation.add(nextButton, BorderLayout.CENTER);
        GridBagConstraints navigationConstraints = formConstraints(4);
        navigationConstraints.insets = new Insets(24, 0, 0, 0);
        questionCard.add(navigation, navigationConstraints);

        page.add(questionCard);
        return page;
    }

    private JPanel buildResultCard() {
        JPanel page = buildPage();
        page.add(buildHeader("Exam Results", "Review your score and answer breakdown"));

        JPanel resultCard = buildFormCard();
        JLabel scoreLabel = new JLabel("", SwingConstants.CENTER);
        scoreLabel.setName("resultScore");
        scoreLabel.setFont(new Font(Font.SANS_SERIF, Font.BOLD, 25));
        scoreLabel.setForeground(BLUE);
        resultCard.add(scoreLabel, formConstraints(0));

        JLabel timeLabel = new JLabel("", SwingConstants.CENTER);
        timeLabel.setName("resultTime");
        timeLabel.setFont(new Font(Font.SANS_SERIF, Font.PLAIN, 15));
        timeLabel.setForeground(MUTED);
        resultCard.add(timeLabel, formConstraints(1));

        JLabel breakdownTitle = new JLabel("Answer breakdown", SwingConstants.LEFT);
        breakdownTitle.setFont(new Font(Font.SANS_SERIF, Font.BOLD, 15));
        breakdownTitle.setForeground(NAVY);
        GridBagConstraints titleConstraints = formConstraints(2);
        titleConstraints.insets = new Insets(18, 0, 6, 0);
        resultCard.add(breakdownTitle, titleConstraints);

        JLabel breakdown = new JLabel();
        breakdown.setName("resultBreakdown");
        breakdown.setFont(new Font(Font.SANS_SERIF, Font.PLAIN, 13));
        breakdown.setForeground(new Color(51, 65, 85));
        JScrollPane breakdownScroll = new JScrollPane(breakdown);
        breakdownScroll.setBorder(BorderFactory.createEmptyBorder());
        breakdownScroll.setPreferredSize(new Dimension(560, 260));
        GridBagConstraints breakdownConstraints = formConstraints(3);
        breakdownConstraints.fill = GridBagConstraints.BOTH;
        breakdownConstraints.weighty = 1;
        resultCard.add(breakdownScroll, breakdownConstraints);

        JButton logoutButton = primaryButton("Logout");
        logoutButton.addActionListener(event -> logout());
        GridBagConstraints logoutConstraints = formConstraints(4);
        logoutConstraints.insets = new Insets(16, 0, 0, 0);
        resultCard.add(logoutButton, logoutConstraints);

        page.add(resultCard);
        return page;
    }

    private JPanel buildPage() {
        JPanel page = new JPanel(new GridBagLayout());
        page.setBackground(BACKGROUND);
        page.setBorder(new EmptyBorder(26, 32, 26, 32));
        return page;
    }

    private JPanel buildHeader(String titleText, String subtitleText) {
        JPanel header = new JPanel(new BorderLayout(0, 6));
        header.setOpaque(false);
        header.setBorder(new EmptyBorder(0, 0, 18, 0));

        JLabel title = new JLabel(titleText);
        title.setFont(new Font(Font.SANS_SERIF, Font.BOLD, 27));
        title.setForeground(NAVY);
        header.add(title, BorderLayout.NORTH);

        JLabel subtitle = new JLabel(subtitleText);
        subtitle.setFont(new Font(Font.SANS_SERIF, Font.PLAIN, 14));
        subtitle.setForeground(MUTED);
        header.add(subtitle, BorderLayout.CENTER);
        return header;
    }

    private JPanel buildFormCard() {
        JPanel card = new JPanel(new GridBagLayout());
        card.setBackground(Color.WHITE);
        card.setBorder(BorderFactory.createCompoundBorder(
                BorderFactory.createLineBorder(new Color(226, 232, 240)),
                new EmptyBorder(24, 28, 24, 28)));
        return card;
    }

    private void addField(JPanel form, String labelText, JTextField field, int row) {
        JLabel label = new JLabel(labelText);
        label.setFont(new Font(Font.SANS_SERIF, Font.BOLD, 13));
        label.setForeground(NAVY);
        form.add(label, formConstraints(row));

        field.setFont(new Font(Font.SANS_SERIF, Font.PLAIN, 15));
        field.setPreferredSize(new Dimension(360, 40));
        field.setBorder(BorderFactory.createCompoundBorder(
                BorderFactory.createLineBorder(new Color(203, 213, 225)),
                new EmptyBorder(7, 10, 7, 10)));
        GridBagConstraints fieldConstraints = formConstraints(row + 1);
        fieldConstraints.insets = new Insets(4, 0, 12, 0);
        form.add(field, fieldConstraints);
    }

    private GridBagConstraints formConstraints(int row) {
        GridBagConstraints constraints = new GridBagConstraints();
        constraints.gridx = 0;
        constraints.gridy = row;
        constraints.weightx = 1;
        constraints.fill = GridBagConstraints.HORIZONTAL;
        constraints.anchor = GridBagConstraints.WEST;
        constraints.insets = new Insets(5, 0, 5, 0);
        return constraints;
    }

    private JButton primaryButton(String text) {
        JButton button = new JButton(text);
        button.setFont(new Font(Font.SANS_SERIF, Font.BOLD, 15));
        button.setForeground(Color.WHITE);
        button.setBackground(BLUE);
        button.setFocusPainted(false);
        button.setBorder(new EmptyBorder(12, 18, 12, 18));
        button.setPreferredSize(new Dimension(180, 44));
        return button;
    }

    private void login() {
        String enteredUsername = loginUsername.getText().trim();
        String enteredPassword = new String(loginPassword.getPassword());
        if (username.equals(enteredUsername) && password.equals(enteredPassword)) {
            profileName.setText(displayName);
            profilePassword.setText("");
            profileMessage.setText(" ");
            loginMessage.setText(" ");
            cardLayout.show(cards, PROFILE_CARD);
        } else {
            loginMessage.setText("Incorrect username or password.");
            loginPassword.setText("");
        }
    }

    private void saveProfileAndStart() {
        String updatedName = profileName.getText().trim();
        String updatedPassword = new String(profilePassword.getPassword());
        if (updatedName.isEmpty()) {
            profileMessage.setText("Please enter a display name.");
            return;
        }
        if (!updatedPassword.isEmpty() && updatedPassword.length() < 4) {
            profileMessage.setText("New password must be at least 4 characters.");
            return;
        }

        displayName = updatedName;
        if (!updatedPassword.isEmpty()) {
            password = updatedPassword;
        }
        profilePassword.setText("");
        beginExam();
    }

    private void beginExam() {
        Arrays.fill(selectedAnswers, -1);
        currentQuestion = 0;
        remainingSeconds = EXAM_DURATION_SECONDS;
        examStartSeconds = remainingSeconds;
        examActive = true;
        timeExpired = false;
        examWelcome.setText("Good luck, " + displayName + "!");
        updateTimerLabel();
        showQuestion();
        cardLayout.show(cards, EXAM_CARD);
        countdownTimer.start();
    }

    private void showQuestion() {
        Question question = QUESTIONS[currentQuestion];
        questionCounter.setText("Question " + (currentQuestion + 1)
                + " of " + QUESTIONS.length);
        questionPrompt.setText("<html><div style='width:530px'>"
                + escapeHtml(question.prompt) + "</div></html>");
        optionGroup.clearSelection();
        for (int index = 0; index < options.length; index++) {
            options[index].setText(question.options[index]);
            options[index].setBackground(Color.WHITE);
            options[index].setForeground(new Color(46, 58, 79));
            options[index].setSelected(selectedAnswers[currentQuestion] == index);
        }
        examMessage.setText("Your answer is saved automatically when selected.");
        previousButton.setEnabled(currentQuestion > 0);
        boolean hasNextQuestion = currentQuestion < QUESTIONS.length - 1;
        nextButton.setText(hasNextQuestion ? "Next" : "Last question");
        nextButton.setEnabled(hasNextQuestion);
    }

    private void navigateQuestion(int direction) {
        int targetQuestion = currentQuestion + direction;
        if (targetQuestion < 0 || targetQuestion >= QUESTIONS.length) {
            return;
        }
        currentQuestion = targetQuestion;
        showQuestion();
    }

    private int findSelectedOption() {
        for (int index = 0; index < options.length; index++) {
            if (options[index].isSelected()) {
                return index;
            }
        }
        return -1;
    }

    private void tickClock() {
        remainingSeconds--;
        updateTimerLabel();
        if (remainingSeconds <= 0) {
            countdownTimer.stop();
            timeExpired = true;
            submitExam();
        }
    }

    private void updateTimerLabel() {
        long minutes = TimeUnit.SECONDS.toMinutes(remainingSeconds);
        long seconds = remainingSeconds % 60;
        timerLabel.setText(String.format("%02d:%02d", minutes, seconds));
        timerLabel.setForeground(remainingSeconds <= 60 ? RED : BLUE);
    }

    private void confirmSubmit() {
        int unanswered = 0;
        for (int answer : selectedAnswers) {
            if (answer == -1) {
                unanswered++;
            }
        }
        String message = unanswered == 0
                ? "Submit your exam now?"
                : "You have " + unanswered + " unanswered question"
                        + (unanswered == 1 ? "" : "s") + ". Submit anyway?";
        int choice = JOptionPane.showConfirmDialog(frame, message,
                "Confirm submission", JOptionPane.YES_NO_OPTION, JOptionPane.QUESTION_MESSAGE);
        if (choice == JOptionPane.YES_OPTION) {
            submitExam();
        }
    }

    private void submitExam() {
        if (!examActive) {
            return;
        }
        examActive = false;
        countdownTimer.stop();
        int score = 0;
        StringBuilder review = new StringBuilder("<html><div style='width:540px'>");

        for (int index = 0; index < QUESTIONS.length; index++) {
            Question question = QUESTIONS[index];
            boolean correct = selectedAnswers[index] == question.correctIndex;
            if (correct) {
                score++;
            }

            review.append("<p><b>Q").append(index + 1).append(". ")
                    .append(escapeHtml(question.prompt)).append("</b><br>");
            if (selectedAnswers[index] == -1) {
                review.append("<font color='#b73131'>Incorrect - no answer selected.</font>");
            } else if (correct) {
                review.append("<font color='#1f7f52'>Correct - ")
                        .append(escapeHtml(question.options[question.correctIndex]))
                        .append("</font>");
            } else {
                review.append("<font color='#b73131'>Incorrect - your answer: ")
                        .append(escapeHtml(question.options[selectedAnswers[index]]))
                        .append("</font><br><font color='#1f7f52'>Correct answer: ")
                        .append(escapeHtml(question.options[question.correctIndex]))
                        .append("</font>");
            }
            review.append("</p>");
        }
        review.append("</div></html>");

        int timeTaken = examStartSeconds - remainingSeconds;
        JLabel scoreLabel = findResultLabel("resultScore");
        JLabel timeLabel = findResultLabel("resultTime");
        JLabel breakdownLabel = findResultLabel("resultBreakdown");
        scoreLabel.setText("Score: " + score + " out of " + QUESTIONS.length);
        timeLabel.setText((timeExpired ? "Time expired - submitted automatically. " : "")
                + "Time taken: " + formatDuration(timeTaken));
        breakdownLabel.setText(review.toString());
        cardLayout.show(cards, RESULT_CARD);
    }

    private JLabel findResultLabel(String name) {
        return findComponentByName(cards, name);
    }

    private JLabel findComponentByName(JPanel parent, String name) {
        for (java.awt.Component component : parent.getComponents()) {
            if (name.equals(component.getName()) && component instanceof JLabel) {
                return (JLabel) component;
            }
            if (component instanceof JPanel) {
                JLabel found = findComponentByName((JPanel) component, name);
                if (found != null) {
                    return found;
                }
            }
            if (component instanceof JScrollPane) {
                java.awt.Component view = ((JScrollPane) component).getViewport().getView();
                if (view instanceof JLabel && name.equals(view.getName())) {
                    return (JLabel) view;
                }
            }
        }
        throw new IllegalStateException("Result component not found: " + name);
    }

    private void logout() {
        loginUsername.setText(username);
        loginPassword.setText("");
        loginDemoHint.setText("Sign in as " + username + " to start another exam.");
        loginMessage.setText(" ");
        cardLayout.show(cards, LOGIN_CARD);
    }

    private void confirmWindowClose() {
        if (!examActive) {
            frame.dispose();
            return;
        }

        int choice = JOptionPane.showConfirmDialog(frame,
                "Are you sure you want to quit? Your exam progress will be lost.",
                "Quit exam?", JOptionPane.YES_NO_OPTION, JOptionPane.WARNING_MESSAGE);
        if (choice == JOptionPane.YES_OPTION) {
            examActive = false;
            countdownTimer.stop();
            frame.dispose();
        }
    }

    private String formatDuration(int totalSeconds) {
        long minutes = TimeUnit.SECONDS.toMinutes(totalSeconds);
        long seconds = totalSeconds % 60;
        return String.format("%d min %02d sec", minutes, seconds);
    }

    private String escapeHtml(String text) {
        return text.replace("&", "&amp;")
                .replace("<", "&lt;")
                .replace(">", "&gt;")
                .replace("\"", "&quot;")
                .replace("'", "&#39;");
    }

    private static final class Question {
        private final String prompt;
        private final String[] options;
        private final int correctIndex;

        private Question(
                String prompt,
                String optionOne,
                String optionTwo,
                String optionThree,
                String optionFour,
                int correctIndex) {
            this.prompt = prompt;
            this.options = new String[]{optionOne, optionTwo, optionThree, optionFour};
            this.correctIndex = correctIndex;
        }
    }
}
