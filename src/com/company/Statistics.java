package com.company;

import java.util.Arrays;
import java.util.List;

/**
 * Created by patrickwang on 2/8/2017.
 */
public class Statistics {

    Double[] data;
    int size;

    public Statistics(List<Double> data)
    {
        this.data = data.toArray(new Double[data.size()]);
        size = data.size();
    }

    public double getMean()
    {
        if (size == 0)
            return 0;
        double sum = 0.0;
        for(double a : data)
            sum += a;
        return sum/size;
    }

    private double getVariance()
    {
        double mean = getMean();
        double temp = 0;
        for(double a :data)
            temp += (a-mean)*(a-mean);
        return temp/(size-1);
    }

    public double getStdDev()
    {
        if(size == 0 | size == 1)
            return 1;

        return Math.sqrt(getVariance());
    }

    public double median()
    {
        Arrays.sort(data);

        if (data.length % 2 == 0)
        {
            return (data[(data.length / 2) - 1] + data[data.length / 2]) / 2.0;
        }
        return data[data.length / 2];
    }
}
