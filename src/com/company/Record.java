package com.company;

import java.util.Date;
/**
 * Created by patrickwang on 2/8/2017.
 */
public class Record {

    private String pid;
    private int timeStage;

    private double slope = 0;
    private String source = null;

    public Record(String pid, int timeStage, double slope, String source){
        this.pid = pid;
        this.timeStage = timeStage;
        this.slope = slope;
        this.source = source;
        SourceList.getInstance().getSource(source).addPost(this);
    }

    public String getPid() {
        return pid;
    }

    public int getTimeStage() {
        return timeStage;
    }

    public double getSlope() {
        return slope;
    }
}
