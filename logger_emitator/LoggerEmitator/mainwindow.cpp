#include <iostream>
#include <Qt>
#include <QDebug>
#include <QString>
#include <QTimer>
#include <QDateTime>
#include "qmath.h"
#include "mainwindow.h"
#include "ui_mainwindow.h"

MainWindow::MainWindow(QWidget *parent) :
    QMainWindow(parent),
    ui(new Ui::MainWindow)
{
    ui->setupUi(this);

    timer = new QTimer(this);
    connect(timer, SIGNAL(timeout()), this, SLOT(timeout()));
    timer->start(1000);
}

void MainWindow::moveEvent(QMoveEvent *e)
{
    QMainWindow::moveEvent(e);
    this->updateLabel();
}

void MainWindow::resizeEvent(QResizeEvent *e)
{
    QMainWindow::resizeEvent(e);
    this->updateLabel();
}

void MainWindow::updateLabel()
{
    QRect geometry = this->frameGeometry();
    QString label = QString("Size: %1x%2\nPosition: %3, %4")
            .arg(geometry.width())
            .arg(geometry.height())
            .arg(geometry.x())
            .arg(geometry.y());

    ui->label->setText(label);
}

void MainWindow::timeout()
{
    int flag = qrand() % 2;

    if (flag) {
        QString now = QDateTime::currentDateTime().toString("yyyy-MM-dd hh:mm:ss");
        QString log_record = QString("LOG | WARNING  | %1 | Message sended in %1.").arg(now);
        std::cout << log_record.toStdString() << std::endl;
    } else {
        std::cout << "Anybody message..." << std::endl;
    }
}

MainWindow::~MainWindow()
{
    delete ui;
}
