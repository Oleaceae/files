package dslabs.shardkv;

import dslabs.framework.Address;
import dslabs.framework.Client;
import dslabs.framework.Result;
import dslabs.framework.testing.Workload;
import dslabs.framework.testing.junit.Lab;
import dslabs.framework.testing.junit.Part;
import dslabs.framework.testing.junit.TestDescription;
import dslabs.framework.testing.junit.RunTests;
import dslabs.framework.testing.junit.SearchTests;
import dslabs.framework.testing.junit.TestPointValue;
import dslabs.framework.testing.junit.UnreliableTests;
import dslabs.framework.testing.search.Search;
import dslabs.kvstore.TransactionalKVStore.MultiGetResult;
import dslabs.kvstore.TransactionalKVStoreWorkload;
import dslabs.shardkv.ShardStoreBaseTest;
import dslabs.shardmaster.ShardMaster.Join;
import dslabs.shardmaster.ShardMaster.Leave;
import dslabs.shardmaster.ShardMaster.Ok;
import java.util.List;
import java.util.Objects;
import org.junit.FixMethodOrder;
import org.junit.Test;
import org.junit.experimental.categories.Category;
import org.junit.runners.MethodSorters;

import static dslabs.framework.testing.StatePredicate.CLIENTS_DONE;
import static dslabs.framework.testing.StatePredicate.RESULTS_OK;
import static dslabs.framework.testing.StatePredicate.resultsHaveType;
import static dslabs.framework.testing.StatePredicate.statePredicate;
import static dslabs.kvstore.KVStoreWorkload.KEY_NOT_FOUND;
import static dslabs.kvstore.KVStoreWorkload.OK;
import static dslabs.kvstore.TransactionalKVStoreWorkload.MULTI_GETS_MATCH;
import static dslabs.kvstore.TransactionalKVStoreWorkload.OK;
import static dslabs.kvstore.TransactionalKVStoreWorkload.multiGet;
import static dslabs.kvstore.TransactionalKVStoreWorkload.multiGetResult;
import static dslabs.kvstore.TransactionalKVStoreWorkload.multiPut;
import static dslabs.kvstore.TransactionalKVStoreWorkload.multiPutOk;
import static dslabs.kvstore.TransactionalKVStoreWorkload.swap;
import static dslabs.kvstore.TransactionalKVStoreWorkload.swapOk;
import static junit.framework.TestCase.assertFalse;

@Lab("4")
@Part(4)
@FixMethodOrder(MethodSorters.NAME_ASCENDING)
public class ShardStorePart3Test extends ShardStoreBaseTest {
    @Test(timeout = 5 * 1000)
    @TestDescription("Single group, simple transactional workload (no swap) - single server")
    @Category(RunTests.class)
    @TestPointValue(10)
    public void test01SingleBasicSingleServer() throws InterruptedException {
        int numGroups = 1, numServersPerGroup = 1, numShardMasters = 1,
                numShards = 2;

        setupStates(numGroups, numServersPerGroup, numShardMasters, numShards);

        runState.start(runSettings);

        joinGroup(1, numServersPerGroup);
        runState.addClientWorker(client(1),
                TransactionalKVStoreWorkload.simpleWorkloadNoSwap);

        runState.waitFor();
        runState.stop();

        runSettings.addInvariant(RESULTS_OK);
    }

    @Test(timeout = 5 * 1000)
    @TestDescription("Multi-group, simple transactional workload (no swap) - single server")
    @Category(RunTests.class)
    @TestPointValue(10)
    public void test02MultiBasicSingleServer() throws InterruptedException {
        int numGroups = 2, numServersPerGroup = 1, numShardMasters = 1,
                numShards = 2;

        setupStates(numGroups, numServersPerGroup, numShardMasters, numShards);

        runState.start(runSettings);

        joinGroup(1, numServersPerGroup);
        joinGroup(2, numServersPerGroup);
        assertConfigBalanced();

        runState.addClientWorker(client(1),
                TransactionalKVStoreWorkload.simpleWorkloadNoSwap);

        runState.waitFor();
        runState.stop();

        runSettings.addInvariant(RESULTS_OK);
    }

    @Test(timeout = 10 * 1000)
    @TestDescription("No progress when groups can't communicate - single server")
    @Category(RunTests.class)
    @TestPointValue(10)
    public void test03NoProgressSingleServer() throws InterruptedException {
        int numServersPerGroup = 1, numShardMasters = 1, numShards = 2;

        setupStates(2, numServersPerGroup, numShardMasters, numShards);

        runState.start(runSettings);
        joinGroup(1, numServersPerGroup);
        joinGroup(2, numServersPerGroup);
        assertConfigBalanced();

        Client client = runState.addClient(client(1));
        sendCommandAndCheck(client,
                multiPut("key1-1", "foo1", "key1-2", "foo2"), multiPutOk());

        // Let the previous transaction result propagate
        Thread.sleep(1000);

        // Client can talk to both groups, but they can't talk to each other
        runSettings.partition(servers(1, numServersPerGroup),
                servers(2, numServersPerGroup));
        for (int g = 1; g <= 2; g++) {
            for (Address server : servers(g, numServersPerGroup)) {
                runSettings.linkActive(client(1), server, true);
                runSettings.linkActive(server, client(1), true);
            }
        }

        // Send command to each group
        sendCommandAndCheck(client,
                multiPut("key2-1", "foo1", "key3-1", "foo2"), multiPutOk());
        sendCommandAndCheck(client,
                multiPut("key2-2", "foo1", "key3-2", "foo2"), multiPutOk());

        // Send command to both
        client.sendCommand(multiPut("key4-1", "foo1", "key4-2", "foo2"));

        Thread.sleep(5000);

        // Make sure the last command didn't get executed
        assertFalse(client.hasResult());
    }

    @Test(timeout = 10 * 1000)
    @TestDescription("Isolation between MultiPuts and MultiGets - single server")
    @Category(RunTests.class)
    @TestPointValue(10)
    public void test04PutGetIsolationSingleServer() throws InterruptedException {
        int numGroups = 2, numServersPerGroup = 1, numShardMasters = 1,
                numShards = 2, numRounds = 100;

        setupStates(numGroups, numServersPerGroup, numShardMasters, numShards);

        runState.start(runSettings);

        joinGroup(1, numServersPerGroup);
        joinGroup(2, numServersPerGroup);
        assertConfigBalanced();

        runState.addClientWorker(client(1),
                TransactionalKVStoreWorkload.builder().commandStrings(
                        "MULTIPUT:key%i#1:foo%i:key%i#2:foo%i")
                                            .resultStrings(OK)
                                            .numTimes(numRounds).build());
        runState.addClientWorker(client(2),
                TransactionalKVStoreWorkload.builder().commandStrings(
                        "MULTIGET:key%i#1:key%i#2").numTimes(numRounds)
                                            .build());

        runState.waitFor();
        runState.stop();

        runSettings.addInvariant(RESULTS_OK).addInvariant(
                resultsHaveType(client(2), MultiGetResult.class))
                   .addInvariant(MULTI_GETS_MATCH);
    }

    private void repeatedPutsGetsInternalSingleServer(boolean moveShards)
            throws InterruptedException {
        int numGroups = 3, numServersPerGroup = 1, numShardMasters = 1,
                numShards = 10, testLengthSecs = 50, nClients = 5;

        setupStates(numGroups, numServersPerGroup, numShardMasters, numShards);

        runState.start(runSettings);

        for (int g = 1; g <= numGroups; g++) {
            joinGroup(g, numServersPerGroup);
        }
        assertConfigBalanced();

        // Startup the clients
        for (int i = 1; i <= nClients; i++) {
            runState.addClientWorker(client(i), TransactionalKVStoreWorkload
                    .differentKeysInfiniteWorkload(numShards), false);
        }

        if (moveShards) {
            Runnable r = moveShards(numGroups, numShards);
            startThread(r);
        }

        Thread.sleep(testLengthSecs * 1000);

        // Shut everything down
        shutdownStartedThreads();
        runState.stop();

        runSettings.addInvariant(RESULTS_OK);
        assertRunInvariantsHold();
        assertMaxWaitTimeLessThan(4000);
    }

    @Test(timeout = 60 * 1000)
    @TestDescription("Repeated MultiPuts and MultiGets, different keys - single server")
    @Category(RunTests.class)
    @TestPointValue(15)
    public void test05RepeatedPutsGetsSingleServer() throws InterruptedException {
        repeatedPutsGetsInternalSingleServer(false);
    }

    @Test(timeout = 60 * 1000)
    @TestDescription("Repeated MultiPuts and MultiGets, different keys - single server")
    @Category({RunTests.class, UnreliableTests.class})
    @TestPointValue(15)
    public void test06RepeatedPutsGetsUnreliableSingleServer() throws InterruptedException {
        runSettings.networkDeliverRate(0.8);
        repeatedPutsGetsInternalSingleServer(false);
    }

    @Test(timeout = 60 * 1000)
    @TestDescription(
            "Repeated MultiPuts and MultiGets, different keys; constant movement - single server")
    @Category({RunTests.class, UnreliableTests.class})
    @TestPointValue(15)
    public void test07ConstantMovementSingleServer() throws InterruptedException {
        runSettings.networkDeliverRate(0.8);
        repeatedPutsGetsInternalSingleServer(true);
    }

    @Test
    @TestDescription("Single client, single group; MultiPut, MultiGet")
    @Category(SearchTests.class)
    @TestPointValue(20)
    public void test08SingleClientSingleGroupSearch() {
        setupStates(1, 1, 1, 10);
        initSearchState.addClientWorker(client(1),
                TransactionalKVStoreWorkload.putGetWorkload);
        singleClientSingleGroupSearch();
    }

    @Test
    @TestDescription("Single client, multi-group; MultiPut, MultiGet")
    @Category(SearchTests.class)
    @TestPointValue(20)
    public void test09SingleClientMultiGroupSearch() {
        setupStates(2, 1, 1, 10);
        initSearchState.addClientWorker(client(1),
                TransactionalKVStoreWorkload.putGetWorkload);
        singleClientMultiGroupSearch();
    }

    private void randomSearch(int numServersPerGroup) {
        setupStates(2, numServersPerGroup, 1, 2);

        Workload ccWorkload = Workload.builder().commands(
                new Join(1, servers(1, numServersPerGroup)),
                new Join(2, servers(2, numServersPerGroup)), new Leave(1))
                                      .results(new Ok(), new Ok(), new Ok())
                                      .build();
        initSearchState.addClientWorker(CCA, ccWorkload);

        initSearchState.addClientWorker(client(1),
                TransactionalKVStoreWorkload.builder().commands(
                        multiPut("foo-1", "X", "foo-2", "Y"))
                                            .results(multiPutOk()).build());

        initSearchState.addClientWorker(client(2),
                TransactionalKVStoreWorkload.builder().commands(
                        multiGet("foo-1", "foo-2")).build());

        searchSettings.maxDepth(1000).maxTimeSecs(20).addInvariant(
                statePredicate("MultiGet returns correct results", s -> {
                    List<Result> results = s.clientWorker(client(2)).results();
                    if (results.isEmpty()) {
                        return true;
                    }
                    if (results.size() > 1) {
                        return false;
                    }
                    Result r = results.get(0);
                    return Objects.equals(r,
                            multiGetResult("foo-1", "X", "foo-2", "Y")) ||
                            Objects.equals(r,
                                    multiGetResult("foo-1", KEY_NOT_FOUND,
                                            "foo-2", KEY_NOT_FOUND));
                })).addInvariant(RESULTS_OK).addPrune(CLIENTS_DONE);

        dfs(initSearchState, searchSettings);
    }

    @Test
    @TestDescription("One server per group random search")
    @Category(SearchTests.class)
    @TestPointValue(20)
    public void test10SingleServerRandomSearch() {
        randomSearch(1);
    }

    @Test(timeout = 5 * 1000)
    @TestDescription("Single group, simple transactional workload (no swap) - multi server")
    @Category(RunTests.class)
    @TestPointValue(10)
    public void test11SingleBasic() throws InterruptedException {
        int numGroups = 1, numServersPerGroup = 3, numShardMasters = 3,
                numShards = 2;

        setupStates(numGroups, numServersPerGroup, numShardMasters, numShards);

        runState.start(runSettings);

        joinGroup(1, numServersPerGroup);
        runState.addClientWorker(client(1),
                TransactionalKVStoreWorkload.simpleWorkloadNoSwap);

        runState.waitFor();
        runState.stop();

        runSettings.addInvariant(RESULTS_OK);
    }

    @Test(timeout = 5 * 1000)
    @TestDescription("Multi-group, simple transactional workload (no swap) - multi server")
    @Category(RunTests.class)
    @TestPointValue(10)
    public void test12MultiBasic() throws InterruptedException {
        int numGroups = 2, numServersPerGroup = 3, numShardMasters = 3,
                numShards = 2;

        setupStates(numGroups, numServersPerGroup, numShardMasters, numShards);

        runState.start(runSettings);

        joinGroup(1, numServersPerGroup);
        joinGroup(2, numServersPerGroup);
        assertConfigBalanced();

        runState.addClientWorker(client(1),
                TransactionalKVStoreWorkload.simpleWorkloadNoSwap);

        runState.waitFor();
        runState.stop();

        runSettings.addInvariant(RESULTS_OK);
    }

    @Test(timeout = 10 * 1000)
    @TestDescription("No progress when groups can't communicate - multi server")
    @Category(RunTests.class)
    @TestPointValue(10)
    public void test13NoProgress() throws InterruptedException {
        int numServersPerGroup = 3, numShardMasters = 3, numShards = 2;

        setupStates(2, numServersPerGroup, numShardMasters, numShards);

        runState.start(runSettings);
        joinGroup(1, numServersPerGroup);
        joinGroup(2, numServersPerGroup);
        assertConfigBalanced();

        Client client = runState.addClient(client(1));
        sendCommandAndCheck(client,
                multiPut("key1-1", "foo1", "key1-2", "foo2"), multiPutOk());

        // Let the previous transaction result propagate
        Thread.sleep(1000);

        // Client can talk to both groups, but they can't talk to each other
        runSettings.partition(servers(1, numServersPerGroup),
                servers(2, numServersPerGroup));
        for (int g = 1; g <= 2; g++) {
            for (Address server : servers(g, numServersPerGroup)) {
                runSettings.linkActive(client(1), server, true);
                runSettings.linkActive(server, client(1), true);
            }
        }

        // Send command to each group
        sendCommandAndCheck(client,
                multiPut("key2-1", "foo1", "key3-1", "foo2"), multiPutOk());
        sendCommandAndCheck(client,
                multiPut("key2-2", "foo1", "key3-2", "foo2"), multiPutOk());

        // Send command to both
        client.sendCommand(multiPut("key4-1", "foo1", "key4-2", "foo2"));

        Thread.sleep(5000);

        // Make sure the last command didn't get executed
        assertFalse(client.hasResult());
    }

    @Test(timeout = 10 * 1000)
    @TestDescription("Isolation between MultiPuts and MultiGets - multi server")
    @Category(RunTests.class)
    @TestPointValue(10)
    public void test14PutGetIsolation() throws InterruptedException {
        int numGroups = 2, numServersPerGroup = 3, numShardMasters = 3,
                numShards = 2, numRounds = 100;

        setupStates(numGroups, numServersPerGroup, numShardMasters, numShards);

        runState.start(runSettings);

        joinGroup(1, numServersPerGroup);
        joinGroup(2, numServersPerGroup);
        assertConfigBalanced();

        runState.addClientWorker(client(1),
                TransactionalKVStoreWorkload.builder().commandStrings(
                        "MULTIPUT:key%i#1:foo%i:key%i#2:foo%i")
                                            .resultStrings(OK)
                                            .numTimes(numRounds).build());
        runState.addClientWorker(client(2),
                TransactionalKVStoreWorkload.builder().commandStrings(
                        "MULTIGET:key%i#1:key%i#2").numTimes(numRounds)
                                            .build());

        runState.waitFor();
        runState.stop();

        runSettings.addInvariant(RESULTS_OK).addInvariant(
                resultsHaveType(client(2), MultiGetResult.class))
                   .addInvariant(MULTI_GETS_MATCH);
    }

    private void repeatedPutsGetsInternalMultiServer(boolean moveShards)
            throws InterruptedException {
        int numGroups = 3, numServersPerGroup = 3, numShardMasters = 3,
                numShards = 10, testLengthSecs = 50, nClients = 5;

        setupStates(numGroups, numServersPerGroup, numShardMasters, numShards);

        runState.start(runSettings);

        for (int g = 1; g <= numGroups; g++) {
            joinGroup(g, numServersPerGroup);
        }
        assertConfigBalanced();

        // Startup the clients
        for (int i = 1; i <= nClients; i++) {
            runState.addClientWorker(client(i), TransactionalKVStoreWorkload
                    .differentKeysInfiniteWorkload(numShards), false);
        }

        if (moveShards) {
            Runnable r = moveShards(numGroups, numShards);
            startThread(r);
        }

        Thread.sleep(testLengthSecs * 1000);

        // Shut everything down
        shutdownStartedThreads();
        runState.stop();

        runSettings.addInvariant(RESULTS_OK);
        assertRunInvariantsHold();
        assertMaxWaitTimeLessThan(4000);
    }

    @Test(timeout = 60 * 1000)
    @TestDescription("Repeated MultiPuts and MultiGets, different keys - multi server")
    @Category(RunTests.class)
    @TestPointValue(20)
    public void test15RepeatedPutsGets() throws InterruptedException {
        repeatedPutsGetsInternalMultiServer(false);
    }

    @Test(timeout = 60 * 1000)
    @TestDescription("Repeated MultiPuts and MultiGets, different keys - multi server")
    @Category({RunTests.class, UnreliableTests.class})
    @TestPointValue(20)
    public void test16RepeatedPutsGetsUnreliableMultiServer() throws InterruptedException {
        runSettings.networkDeliverRate(0.8);
        repeatedPutsGetsInternalMultiServer(false);
    }

    @Test(timeout = 60 * 1000)
    @TestDescription(
            "Repeated MultiPuts and MultiGets, different keys; constant movement - multi server")
    @Category({RunTests.class, UnreliableTests.class})
    @TestPointValue(20)
    public void test17ConstantMovement() throws InterruptedException {
        runSettings.networkDeliverRate(0.8);
        repeatedPutsGetsInternalMultiServer(true);
    }

    @Test
    @TestDescription("Multiple servers per group random search")
    @Category(SearchTests.class)
    @TestPointValue(20)
    public void test18MultiServerRandomSearch() {
        randomSearch(3);
    }
}