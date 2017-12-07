package com.company;

import java.util.ArrayList;

/**
 * Created by patrickwang on 2/8/2017.
 */
public class Source {

    private ArrayList<Double> slopeMeanList;
    private ArrayList<Double> slopeStdList;
    private String name;
    private ArrayList<Record> recordList;

    public Source(String name){
        this.name = name;
        slopeMeanList = new ArrayList<Double>();
        slopeStdList = new ArrayList<Double>();
        recordList = new ArrayList<Record>();
    }

    public String getName(){
        return name;
    }

    public String toString(){
        return name;
    }

    public void addPost(Record record){
        recordList.add(record);
    }

    public void updatePost(Record record){
//        addPost() method is used when first constructing postlists,
//        updatePost() method should be used when every time a new posts were added.
//        therefore, calculate() should be performed.
        recordList.add(record);
        this.calculate();
    }

//  calculate the avg and std of 12 different time slope(stage)
    public void calculate(){

        for(int stage = 0; stage < 12; stage++){

            ArrayList<Double> stageList = new ArrayList<>();
            for(int i = 0; i < recordList.size(); i++){

                if(recordList.get(i).getTimeStage()-1 == stage){

                    stageList.add(recordList.get(i).getSlope());
                }

            }
            Statistics stats = new Statistics(stageList);
            slopeMeanList.add(stats.getMean());
            slopeStdList.add(stats.getStdDev());

        }
    }

    public String getMean(){
//        before getting tables, calculate
        calculate();
        String result = this.name;
        result += ",";
        for(int i = 0; i < slopeMeanList.size(); i++){

            result += slopeMeanList.get(i);
            result += ",";
        }
        return result + "\n";
    }

    public String getStd(){
        String result = this.name;
        result += ",";

        for(int i = 0; i < slopeStdList.size(); i++){

            result += slopeStdList.get(i);
            result += ",";
        }
        return result + "\n";
    }

}
