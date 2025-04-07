package dslabs.atmostonce;

import dslabs.framework.Application;
import dslabs.framework.Command;
import dslabs.framework.Result;
import lombok.EqualsAndHashCode;
import lombok.Getter;
import lombok.NonNull;
import lombok.RequiredArgsConstructor;
import lombok.ToString;

import java.util.HashMap;
import dslabs.framework.Address;

@EqualsAndHashCode
@ToString
@RequiredArgsConstructor
public final class AMOApplication<T extends Application> implements Application {
  @Getter @NonNull private final T application;

  // Your code here...
  private HashMap<Address, AMOResult> store = new HashMap<>();

  @Override
  public AMOResult execute(Command command) {
    if (!(command instanceof AMOCommand)) {
      throw new IllegalArgumentException();
    }
    
    AMOCommand amoCommand = (AMOCommand) command;



    // Your code here...
    // Check if it's an old request
    if (this.alreadyExecuted(amoCommand)) {
      // System.out.println("Command " + amoCommand.id() + " from client " + amoCommand.address() + " executed");
      return this.store.get(amoCommand.address());
    }

    // Execute command
    AMOResult amoresult =  new AMOResult(
      this.application.execute(amoCommand.command()),
      amoCommand.id()
    );
      
      
    // Mark as executed
    this.store.put(amoCommand.address(), amoresult);
    return amoresult;
  }

  public Result executeReadOnly(Command command) {
    if (!command.readOnly()) {
      throw new IllegalArgumentException();
    }

    if (command instanceof AMOCommand) {
      return execute(command);
    }

    return application.execute(command);
  }

  public boolean alreadyExecuted(AMOCommand amoCommand) {
    // Your code here...
    AMOResult save_res = this.store.get(amoCommand.address());
    if (save_res != null && amoCommand.id() <= save_res.id()) {
      return true;
    }
    return false;
  }
}
