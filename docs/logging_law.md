# LOGGING LAWS

### TRACE
--- 
nearly line by line execution of code and values used in their operations.
- how an HTTP request is served
- runtime benchmarks
- parameter values that is being used in a process (not sensitive info)


### DEBUG
--- 
everything that couldn't be included in INFO goes here. startup of components and logging values for major component configurations. basically, information important for troubleshooting, and usually suppressed in normal day-to-day operation
- active processes like starting up of component
- nested classes, composition logs of internal classes
- web api logs on request.response values


### INFO
---
general logs not so important but not so wasteful either. Just a generic indicator or information abstraction for log
levels below it. day-to-day operation as "proof" that program is performing its function as designed.
- successful execution of a major component.method()
- major non-error events, external signals (SIGINT)
- consumer level logs


### WARN
--- 
error that suggest warning of a mis-step  or slight error. out-of-nominal but recoverable situation, *or* coming upon something that may result in future problems
- thread utilization
- server overload
- memory occupying by unused variables


### ERROR
---
error in normal functionality of program that requires attention but doesn't kill the application. For example;
- incorrect configuration
- invalid api call
- runtime exception handles


### FATAL / CRITICAL
---
severe errors that cause obstruction in normal running of the program and cannot be avoided. For example;
- thread or process start / join failure
- critical component startup failure
- deadlocks
- hardware errors