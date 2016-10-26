#include "mainwindow.h"
#include <QApplication>
#include <QTimer>

int main(int argc, char *argv[])
{
    QApplication a(argc, argv);
    MainWindow w;

    QTimer::singleShot(2000, &w, SLOT(show()));

    return a.exec();
}
