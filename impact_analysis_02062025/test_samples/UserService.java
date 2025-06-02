import org.springframework.stereotype.Service;
import org.springframework.beans.factory.annotation.Autowired;

@Service
public class UserService extends BaseService implements UserApi {
    @Autowired
    private UserRepository userRepository;

    public UserService() {}

    @Autowired
    public UserService(UserRepository userRepository, EmailService emailService) {
        this.userRepository = userRepository;
        emailService.sendWelcome();
    }

    public void processUser(User user) {
        Order order = new Order();
        userRepository.save(user);
    }
}
