package com.company;

import java.util.ArrayList;
/**
 * Created by patrickwang on 2/8/2017.
 */
public class SourceList {
    private static SourceList ourInstance = new SourceList();

    private ArrayList<Source> list;

    public static SourceList getInstance() {
        return ourInstance;
    }

    private SourceList() {
        list = new ArrayList<>();
    }

    public void addSource(Source source){
        list.add(source);
    }

    public Source getSource(String name){

        for(Source source:this.list)
            if(name.equals(source.getName()))
                return source;

//        if source not found, create a new one.
        addSource(new Source(name));
        return getSource(name);
    }

    public String getMeanTable(){
//        forgive my hard coding, too lazy to write a for loop...
//        return csv of mean baseline
        String result = "source,1,2,3,4,5,6,7,8,9,10,11,12\n";

        for(Source source:this.list)
            result += source.getMean();

        return result;
    }

    public String getStdTable(){
//        return csv of std baseline
        String result = "source,1,2,3,4,5,6,7,8,9,10,11,12\n";

        for(Source source:this.list)
            result += source.getStd();

        return result;
    }


}
