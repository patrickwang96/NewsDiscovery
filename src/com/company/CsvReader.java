package com.company;

import java.io.BufferedReader;
import java.io.FileNotFoundException;
import java.io.FileReader;
import java.io.IOException;
import java.io.File;
import java.io.FileWriter;
import java.io.BufferedWriter;

/**
 * Created by patrickwang on 3/8/2017.
 */
public class CsvReader {

    public static void readCsv(String filename){

        try {
            BufferedReader reader = new BufferedReader(new FileReader(filename));
            reader.readLine(); //first line is not used
            String line = null;
            while((line=reader.readLine()) != null){
                String item[] = line.split(",");
                String pid = item[0];
                double slope = Double.parseDouble(item[1]);
                String source = item[3];
//                int stage = Integer.parseInt(item[3]);
                int stage = (int)Double.parseDouble(item[2]);
                Record tmp = new Record(pid,stage,slope,source);
            }
        } catch (FileNotFoundException e) {
            e.printStackTrace();
        } catch (IOException e) {
            e.printStackTrace();
        } catch (Exception e){
            e.printStackTrace();
        }
    }

    public static void writeAvg(String address){

        SourceList controller = SourceList.getInstance();

        try{
            // Create new file
            String content = controller.getMeanTable();
            File file = new File(address);

            // If file doesn't exists, then create it
            if (!file.exists()) {
                file.createNewFile();
            }

            FileWriter fw = new FileWriter(file);
            BufferedWriter bw = new BufferedWriter(fw);

            // Write in file
            bw.write(content);

            // Close connection
            bw.close();
        }
        catch(Exception e){
            System.out.println(e);
        }


    }

    public static void writeStd(String address){

        SourceList controller = SourceList.getInstance();

        try{
            // Create new file
            String content = controller.getStdTable();
            File file = new File(address);

            // If file doesn't exists, then create it
            if (!file.exists()) {
                file.createNewFile();
            }

            FileWriter fw = new FileWriter(file);
            BufferedWriter bw = new BufferedWriter(fw);

            // Write in file
            bw.write(content);

            // Close connection
            bw.close();
        }
        catch(Exception e){
            System.out.println(e);
        }


    }
}
