import matplotlib.pyplot as plt
from mpl_toolkits.mplot3d import axes3d
import numpy as np
import csv
from estimate import estimatePrice

def estimatePrice(t0, t1, mileage, param):
    normailzed = t0 + t1 * (mileage - param[1]) / (param[0] - param[1])
    return normailzed * (param[2] - param[3]) + param[3]

def lossFunction(t0, t1, mileages, prices):
    loss = 0.0
    for mileage, price in zip(mileages, prices):
        loss += (price - (t0 + t1 * mileage)) ** 2
    return loss / len(mileages)

def gradientDescent(t0, t1, learningRate, loss, mileages, prices):
    s0, s1 = [0.0, 0.0]
    for mileage, price in zip(mileages, prices):
        s0 += (t0 + t1 * mileage) - price
        s1 += ((t0 + t1 * mileage) - price) * mileage
    if loss > lossFunction(t0 - learningRate * s0 / len(mileages), t1 - learningRate * s1 / len(mileages), mileages, prices):
        t0 -= learningRate * s0 / len(mileages)
        t1 -= learningRate * s1 / len(mileages)
        loss = lossFunction(t0, t1, mileages, prices) 
        learningRate *= 1.04
    else:
        learningRate *= 0.6
    return t0, t1, learningRate, loss

def train(learningRate, epoch, mileages, prices, t0History, t1History):
    t0, t1 = [0.0, 0.0]
    loss = lossFunction(t0, t1, mileages, prices)
    for i in range(0, epoch):
        t0, t1, learningRate, loss = gradientDescent(t0, t1, learningRate, loss, mileages, prices) 
        if i % 10 == 0:
            t0History.append(t0)
            t1History.append(t1)
    return t0, t1
 
def drawLoss(mileages, prices, t0History, t1History):
    plt.figure(2)
    X, Y = np.meshgrid(np.linspace(-0.2, 1.5, 100), np.linspace(-1.6, 0.4, 100))
    Z = (prices[0] - (X + Y * mileages[0])) ** 2
    for mileage, price in zip(mileages, prices):
        Z += (price - (X + Y * mileage)) ** 2
    Z -= (prices[0] - (X + Y * mileages[0])) ** 2
    Z /= len(mileages)
    ax = plt.axes(projection='3d')
    ax.plot_surface(X, Y, Z, cmap='viridis', alpha=0.9)
    cost = []
    for t0, t1 in zip(t0History, t1History):
        ax.scatter(t0, t1, lossFunction(t0, t1, mileages, prices), c='red')
        cost.append(lossFunction(t0, t1, mileages, prices))
    ax.plot(t0History, t1History, cost, c='red')
    ax.set_zlim(0, 0.5)
    ax.set_xlabel('t0')
    ax.set_ylabel('t1')
    ax.set_zlabel('cost')

def main():
    learningRate, epoch = [0.4, 500]
    mileages = []
    prices = []
    t0History = [0.0]
    t1History = [0.0]
    # file
    with open('data.csv', 'r', encoding='utf-8') as file:
        csvReader = csv.reader(file)
        for row in csvReader:
            if (row[0] != 'km'):
                mileages.append(float(row[0]))
                prices.append(float(row[1]))
    # figure 1
    plt.figure(1)
    plt.xlabel('mileage')
    plt.ylabel('price')
    plt.scatter(mileages, prices, s=10, c='green')
    # param
    param = [max(mileages), min(mileages), max(prices), min(prices)]
    for i in range(0, len(mileages)):
        mileages[i] = (mileages[i] - param[1]) / (param[0] - param[1])
        prices[i] = (prices[i] - param[3]) / (param[2] - param[3])
    # train
    t0, t1 = train(learningRate, epoch, mileages, prices, t0History, t1History)
    print('loss: ', lossFunction(t0, t1, mileages, prices))
    print('t0:', t0, '   t1:', t1)
    # save result to file 'thetas.csv'
    with open("thetas.csv", 'w') as file:
        csvWriter = csv.writer(file)
        csvWriter.writerow([t0, t1])
    # draw
    plt.plot([param[1], param[0]], [estimatePrice(t0, t1, param[1], param), estimatePrice(t0, t1, param[0], param)], c='red')
    drawLoss(mileages, prices, t0History, t1History)
    plt.tight_layout()
    plt.show()

if __name__ == "__main__":
    main()