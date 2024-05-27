import sys
from PyQt5.QtWidgets import *
from PyQt5.QtWebEngineWidgets import QWebEngineView

from datetime import date
import csv

class MainWindow(QMainWindow):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.setWindowTitle('Cycling Calorie Calculator')

        self.setFixedSize(800,600)
        centralWidget = QWidget()

        self.formGroupBox = QGroupBox("Form 1")
        self.formGroupBox.setFixedHeight(180)
        
        self.weightInput = QDoubleSpinBox()
        self.weightInput.setDecimals(1)
        self.weightInput.setRange(0, 200)
        self.weightInput.setValue(94.0)
        self.weightInput.setSingleStep(0.1)

        self.distanceInput = QDoubleSpinBox()
        self.distanceInput.setDecimals(2)
        self.distanceInput.setValue(11.89)
        self.distanceInput.setSingleStep(0.01)
        # self.distanceInput.valueChanged.connect(self.updateSpeed)

        self.durationInput = QSpinBox()
        self.durationInput.setRange(1, 120)
        self.durationInput.setValue(40)
        # self.durationInput.valueChanged.connect(self.updateSpeed)

        self.speedInput = QDoubleSpinBox()
        # self.speedInput.valueChanged.connect(self.updateDuration)
        self.speedInput.setDecimals(2)
        self.speedInput.setSingleStep(0.01)
        self.speedInput.setRange(0, 40)
        self.speedInput.setValue(18.3)

        self.createForm()

        self.htmlView = QWebEngineView()
        self.resize(800,600)

        self.buttonBox = QDialogButtonBox(QDialogButtonBox.Ok)
        self.buttonBox.accepted.connect(self.saveEntry)
        # self.buttonBox.rejected.connect(self.reject)
        mainLayout = QVBoxLayout()

        mainLayout.addWidget(self.formGroupBox)
        mainLayout.addWidget(self.buttonBox)
        mainLayout.addWidget(self.htmlView)


        centralWidget.setLayout(mainLayout)

        self.setCentralWidget(centralWidget)
        self.create_line_chart()

    def updateDuration(self):
        duration = self.distanceInput.value() / self.speedInput.value() * 60
        self.durationInput.setValue(int(duration))

    def updateSpeed(self):
        speed = self.distanceInput.value() / (self.durationInput.value() / 60)
        self.speedInput.setValue(speed)

    def getMETbySpeed(self, speed):
        # Quadratic function approximated from MET values above
        speed = 1 / 1.6 * speed
        return 0.032 * speed * speed + 0.02 * speed + 2.6

    def createForm(self):
        layout = QFormLayout()
        layout.addRow(QLabel("Weight (kg)"), self.weightInput)
        layout.addRow(QLabel("Distance (km)"), self.distanceInput)
        layout.addRow(QLabel("Duration (minutes)"), self.durationInput)
        layout.addRow(QLabel("Speed (kph)"), self.speedInput)
        self.formGroupBox.setLayout(layout)

    def saveEntry(self):
        f = open("./entries.csv", 'r+', newline='')
        reader = csv.reader(f, delimiter=',', quotechar='|')
        for row in reader:
            print(','.join(row))
        
        writer = csv.writer(f, delimiter=',', quotechar='|', quoting=csv.QUOTE_MINIMAL)
        writer.writerow([
            self.weightInput.value(),
            self.distanceInput.value(),
            self.durationInput.value(),
            self.speedInput.value(),
            round(self.calculateCalories(), 2),
            date.today()
        ])
        f.flush()
        f.close()
        self.create_line_chart()

    def calculateCalories(self):
        MET = self.getMETbySpeed(self.speedInput.value())
        weight = self.weightInput.value()
        duration = (self.durationInput.value() / 60)
        return MET * weight * duration

    def create_line_chart(self):
        date = ['Date']
        weight = ["Weight"]
        distance = ["Distance"]
        duration = ["Duration"]
        speed = ["Speed"]
        calories = ["Calories"]

        f = open("./entries.csv", 'r+', newline='')
        reader = csv.reader(f, delimiter=',', quotechar='|')
        for row in reader:
            weight.append(row[0])
            distance.append(row[1])
            duration.append(row[2])
            speed.append(row[3])
            calories.append(row[4])
            date.append(row[5])
        f.close()

        source_data = [date, weight, distance, duration, speed, calories]

        the_html_content ='''
<!DOCTYPE html>
<html style="height: 50%; width:50%">
    <head>
        <meta charset="utf-8">
    </head>
    <body style="
        width: 800px;
        height: 300px;
        overflow: hidden;
        padding: 0;
        margin: 0;
        display:flex;
        align-items:center;
        justify-content:center;
    ">
        <div id="container" style="width: 80%; height: 80%"></div>
        <script type="text/javascript" src="https://cdn.jsdelivr.net/npm/echarts@5/dist/echarts.min.js"></script>
        <script type="text/javascript">
var dom = document.getElementById("container");
var myChart = echarts.init(dom);
var app = {};
var option;
setTimeout(function () {
    option = {
        legend: {},
        tooltip: {
            trigger: 'axis',
            showContent: false,
            axisPointer: {
                type: 'cross'
            }
        },
        dataset: {
            source: '''+ '{}'.format(source_data) +'''
        },
        xAxis: {type: 'category'},
        yAxis: {gridIndex: 0},
        series: [
            {type: 'line', smooth: true, seriesLayoutBy: 'row', emphasis: {focus: 'series'}},
            {type: 'line', smooth: true, seriesLayoutBy: 'row', emphasis: {focus: 'series'}},
            {type: 'line', smooth: true, seriesLayoutBy: 'row', emphasis: {focus: 'series'}},
            {type: 'line', smooth: true, seriesLayoutBy: 'row', emphasis: {focus: 'series'}},
            {type: 'line', smooth: true, seriesLayoutBy: 'row', emphasis: {focus: 'series'}},
           
        ]
    };
    myChart.setOption(option);
});
if (option && typeof option === 'object') {
    myChart.setOption(option);
}
        </script>
    </body>
</html>
        '''

        self.htmlView.setHtml(the_html_content)


if __name__ == '__main__':
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec())