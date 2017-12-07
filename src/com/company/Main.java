package com.company;
//import java.util.Date;


public class Main {

    public static void main(String[] args) {
	// write your code here
//        System.out.println("hello");

        SourceList controller = SourceList.getInstance();
        CsvReader.readCsv("get_baseline/log.csv");

        CsvReader.writeAvg("get_baseline/avg_baseline.csv");
        CsvReader.writeStd("get_baseline/std_baseline.csv");
    }

}
