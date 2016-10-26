#ifndef MAINWINDOW_H
#define MAINWINDOW_H

#include <QMainWindow>
#include <QTimer>

namespace Ui {
class MainWindow;
}

class MainWindow : public QMainWindow
{
    Q_OBJECT

public:
    explicit MainWindow(QWidget *parent = 0);
    ~MainWindow();

protected:
    void moveEvent(QMoveEvent *e);
    void resizeEvent(QResizeEvent *e);
    void updateLabel();
private:
    Ui::MainWindow *ui;
    QTimer *timer;

private slots:
    void timeout();
};

#endif // MAINWINDOW_H
