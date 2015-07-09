package admin.cbas.eict.de;

import java.text.DateFormat;
import java.util.Date;
import java.util.HashMap;
import java.util.Map;

public class LoggingAuthorityAPI {
	
	static String url;
	static String output = "";
	static Object credentials[];
	
	public static void setHostAndPort(String host, int port)
	{
		url = "https://"+host+":"+port+"/logging";
	}

	
	@SuppressWarnings("unchecked")
	public static LogEvent[] lookupAll()
	{
		Map<String, Object> options = new HashMap<String, Object>();
        Object params[] = new Object[]{"all", options};                
		
        Map<String, Object> rsp = FAPIClient.execute(url, "lookup", params);
		
        Integer code = (Integer)rsp.get("code");
        if (code.intValue() != 0)
        {
        	output = (String)rsp.get("output");
        	return null;
        }
        Object[] values = (Object[]) rsp.get("value");
        LogEvent logs[] = new LogEvent[values.length]; 
        
        for(int i=0; i<values.length; i++)
        {
        	Map<String, Object> event = (Map<String, Object>) values[i];
        	String subject = (String) event.get("ACTOR");
        	String action = (String) event.get("METHOD");
        	double ts = ((Double) event.get("TIMESTAMP")).doubleValue();
        	Object target = event.get("TARGET");
        	String object;
        	if (target == null)
        		object = "null";
        	else if(target instanceof String)
        		object = (String) target;
        	else
        	{
        		Map<String, String> targetMap = (Map<String, String>) target;
        		object = targetMap.values().toString();
        	}
        	
        	Map<String, Object> opts = (Map<String, Object>)event.get("OPTIONS");        	
        	
        		
        	logs[i] = new LogEvent(subject, object, action, ts, opts);	
        }
        
        return logs;
	}

	
	
	static class LogEvent implements Comparable<LogEvent>{
		String subject="", object="", action="", params="";
		Date timestamp;
		
		public LogEvent(String sub, String obj, String act, double ts, Map<String, Object> opts)
		{
			if(sub != null)
			{
				int i = sub.lastIndexOf('+');
				if(i>=0)
					subject = sub.substring(i+1);
				else
					subject = sub;
			}
			if(obj != null)
			{
				int i = obj.lastIndexOf('+');
				int j = obj.lastIndexOf('+', i-1);
				if(j>0)
					object = obj.substring(j+1).replace('+', ':');
				else
					object  = obj;
			}
			
			action  = act;
			if(act != null && act.equals("modify_membership"))
			{
				String key = opts.keySet().iterator().next();
				Object[] list = (Object[]) opts.get(key);
				@SuppressWarnings("unchecked")
				Map<String, String> dict = (Map<String, String>) list[0];
				String objType = obj.contains("project")?"PROJECT":"SLICE";
				String role = dict.get(objType+"_ROLE");
				String urn = dict.get(objType+"_MEMBER");
				String username = urn==null?"":urn.substring(urn.lastIndexOf('+')+1);
				
				if(key.equals("members_to_change"))
				{
					params = username+" -> "+role;
				}
				else if(key.equals("members_to_add"))
				{
					params = "Add "+username+(role==null?"":" as "+role);
				}
				else
				{
					params = "Remove "+ username;
				}
			}
			
			timestamp = new Date((long) (ts*1000));
		}
		
		public String[] getEntry(DateFormat df)
		{
			return new String[]{df.format(timestamp), subject, object, action, params};
		}
		
		public int compareTo(LogEvent e) {			
			return this.timestamp.compareTo(e.timestamp);
		}
		
	}

	
	
	
}



