package admin.cbas.eict.de;

import java.awt.Color;
import java.awt.Component;

import javax.swing.JTable;
import javax.swing.table.TableCellRenderer;
import javax.swing.table.TableModel;

public class ColoredJTable extends JTable {
	
	/**
	 * 
	 */
	private static final long serialVersionUID = 2104761965641668453L;
	Color alternate = new Color(227, 227, 227); //grey
	Color sliceColor =  new Color(128, 0, 128); //dark purple
	Color projectColor = new Color(0, 128, 0);  //dark green
	Color keyColor = new Color(255, 0, 0);  //dark green
	Color userColor = Color.blue;
	TableModel model;
	
    
    public ColoredJTable(TableModel model)
    {
    	super(model);
    	this.model = model;
    }

    public Component prepareRenderer(TableCellRenderer renderer, int r, int c) {
        
    	Component stamp = super.prepareRenderer(renderer, r, c);
    	
    	if( r == this.getSelectedRow())
    	{
    		stamp.setBackground(new Color(57, 105, 138));
    		stamp.setForeground(Color.white);
    	}
    	else
    	{
	        if (r % 2 == 0)
	            stamp.setBackground(alternate);
	        else
	            stamp.setBackground(this.getBackground());

	        int row = convertRowIndexToModel(r);
	        int column = convertColumnIndexToModel(c);    	                
	        
	        //Default font color
	        stamp.setForeground(Color.BLACK);
	        
	        //Color coding for column 2 only
	        if( column == 2) //Object Column
	        {
	
	        	String value = (String) model.getValueAt(row, column);        	
	        	if(value.startsWith("slice"))
	        		stamp.setForeground(sliceColor);
	        	else if(value.startsWith("project"))
	        		stamp.setForeground(projectColor);
	        	else if(value.startsWith("user"))
	        		stamp.setForeground(userColor);        	
	        	else if(value.startsWith("key"))
	        		stamp.setForeground(keyColor);        	
	        }
    	}
        	
         
        return stamp;
    }
}
