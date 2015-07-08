package admin.cbas.eict.de;

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
        		
        	logs[i] = new LogEvent(subject, object, action, ts);	
        }
        
        return logs;
	}

	
	
	static class LogEvent{
		String subject, object, action;
		Date timestamp;
		
		public LogEvent(String sub, String obj, String act, double ts)
		{
			subject = sub;
			object  = obj;
			action  = act;
			timestamp = new Date((long) (ts*1000));
		}
		
		public String[] getEntry()
		{
			return new String[]{timestamp.toString(), subject, object, action};
		}
	}

	
	
	
}



