#include <fstream>
#include <string>
#include <vector>
#include <algorithm>
#include <random>
#include <cstdlib>
#include <ctime>
#include <map>
#include "SCP_Base/CHS.hpp"
#include <boost/python.hpp>
#include "python/include/boost/python/suite/indexing/vector_indexing_suite.hpp"
#include "python/include/boost/python/suite/indexing/map_indexing_suite.hpp"

//using namespace std;
using namespace boost::python;



BOOST_PYTHON_MODULE (pyevstation) //导出的module 名字
{
    def("Change_Use_Seed", Change_Use_Seed);
    def("Get_Car_Flow_Dir", Get_Car_Flow_Dir);
    class_<std::map<int, float> >("Map_int_float")
            .def(map_indexing_suite<std::map<int, float> >());

    class_<std::map<std::string, SlowPile> >("Map_int_float")
            .def(map_indexing_suite<std::map<std::string, SlowPile> >());

    class_<std::map<std::string, std::map<int, float> > >("Map_string_int_float")
            .def(map_indexing_suite<std::map<std::string, std::map<int, float> > >());

    class_<std::vector<int> >("Vector_int")
            .def(vector_indexing_suite<std::vector<int> >());

    class_<std::vector<float> >("Vector_float")
            .def(vector_indexing_suite<std::vector<float> >());

    class_<std::vector<double> >("Vector_double")
            .def(vector_indexing_suite<std::vector<double> >());


    class_<RandomUtil>("RandomUtil")
            .def("uniform_rand", &RandomUtil::uniform_rand);

//    class_<PrintUtil>("PrintUtil")
//            .def("Print_Two_Dimension_Map", &PrintUtil::Print_Two_Dimension_Map<>)
//            .def("Print_Map", &PrintUtil::Print_Map)
//            .def("Print_Vector", &PrintUtil::Print_Vector)
//            .def("Print_Two_Dimension_Vector", &PrintUtil::Print_Two_Dimension_Vector);
//
//    class_<Read2Vector>("Read2Vector")
//            .def("read", &Read2Vector::read);


    class_<Station>("Station")
            .def_readwrite("charge_number", &Station::charge_number)
            .def_readwrite("situation", &Station::situation)
            .def_readwrite("station_time_hole", &Station::station_time_hole)
            .def_readwrite("load_assigned", &Station::load_assigned)
            .def_readwrite("flow_in_number", &Station::flow_in_number)
            .def_readwrite("no_charge_list", &Station::no_charge_list)
            .def_readwrite("no_charge_number", &Station::no_charge_number)
            .def_readwrite("empty_list", &Station::empty_list)
            .def_readwrite("empty_number", &Station::empty_number)
            .def_readwrite("min_power", &Station::min_power)
            .def_readwrite("max_power", &Station::max_power)
            .def_readwrite("charge_power", &Station::charge_power)
            .def_readwrite("car_number", &Station::car_number)
            .def_readwrite("show", &Station::show)
            .def_readwrite("wait", &Station::wait)
            .def_readwrite("line", &Station::line)
            .def_readwrite("constant_charging", &Station::constant_charging)
            .def_readwrite("max_line", &Station::max_line)

            .def("print_situation", &Station::print_situation);

    class_<ChargePositionBase>("ChargePositionBase", init<int, Station *>())
            .def_readwrite("position", &ChargePositionBase::position)
            .def_readwrite("arrive_soc", &ChargePositionBase::arrive_soc)
            .def_readwrite("target_soc", &ChargePositionBase::target_soc)
            .def_readwrite("current_soc", &ChargePositionBase::current_soc)
            .def_readwrite("current_power", &ChargePositionBase::current_power)
            .def_readwrite("must_charge", &ChargePositionBase::must_charge)
            .def_readwrite("emergency", &ChargePositionBase::emergency)
            .def_readwrite("stay_time", &ChargePositionBase::stay_time)
            .def_readwrite("already_stay_time", &ChargePositionBase::already_stay_time)


            .def("pl_reset", &ChargePositionBase::pl_reset)
            .def("reset_position", &ChargePositionBase::reset_position)
            .def("occupy_charge", &ChargePositionBase::occupy_charge);

    class_<StationBase>("StationBase", init<int, std::string, bool>())
            //////////////////////////// wrapper start
            .def("catch_load", &StationBase::catch_load_wrapper1)
            .def("catch_load", &StationBase::catch_load_wrapper2)
                    //////////////////////////// wrapper end
            .def("calculate_output", &StationBase::calculate_output)
            .def("print_situation", &StationBase::print_situation)
            .def("tell_empty", &StationBase::tell_empty)
            .def("tell_chargeable", &StationBase::tell_chargeable)
            .def("assign_car", &StationBase::assign_car);

    class_<UtilSlow>("UtilSlow")
            //////////////////////////// wrapper start
            .def("slow_time_to_power", &UtilSlow::slow_time_to_power_wrapper1)
            .def("slow_time_to_power", &UtilSlow::slow_time_to_power_wrapper2)
            .def("slow_time_to_soc", &UtilSlow::slow_time_to_soc_wrapper1)
            .def("slow_time_to_soc", &UtilSlow::slow_time_to_soc_wrapper2)
            .def("slow_soc_to_time", &UtilSlow::slow_soc_to_time_wrapper1)
            .def("slow_soc_to_time", &UtilSlow::slow_soc_to_time_wrapper2)
        //////////////////////////// wrapper end
            ;

    class_<UtilFast>("UtilFast")
            //////////////////////////// wrapper start
            .def("fast_time_to_power", &UtilFast::fast_time_to_power_wrapper1)
            .def("fast_time_to_power", &UtilFast::fast_time_to_power_wrapper2)
            .def("fast_time_to_soc", &UtilFast::fast_time_to_soc_wrapper1)
            .def("fast_time_to_soc", &UtilFast::fast_time_to_soc_wrapper2)
            .def("fast_soc_to_time", &UtilFast::fast_soc_to_time_wrapper1)
            .def("fast_soc_to_time", &UtilFast::fast_soc_to_time_wrapper2)
        //////////////////////////// wrapper end
            ;

    class_<PoissonNumber>("PoissonNumber")
            .def("give_car_number_wrt_poisson", &PoissonNumber::give_car_number_wrt_poisson)
            .def("ev_car_number_wrt_poisson_slow", &PoissonNumber::ev_car_number_wrt_poisson_slow)
            .def("ev_car_number_wrt_poisson_fast", &PoissonNumber::ev_car_number_wrt_poisson_fast)
            .def("hv_car_number_wrt_poisson", &PoissonNumber::hv_car_number_wrt_poisson);

    class_<CarArriveRandom>("CarArriveRandom")
            .def("mk_soc", &CarArriveRandom::mk_soc)
            .def("mk_late_time", &CarArriveRandom::mk_late_time)
                    //////////////////////////// wrapper start
            .def("init_station_car_number", &CarArriveRandom::init_station_car_number_wrapper1)
            .def("init_station_car_number", &CarArriveRandom::init_station_car_number_wrapper2)
            .def("init_station_car_number", &CarArriveRandom::init_station_car_number_wrapper3)
            .def("init_station_car_number", &CarArriveRandom::init_station_car_number_wrapper4)
        //////////////////////////// wrapper end
            ;

    class_<SlowPile>("SlowPile", init<int, Station *>())
            .def("add_car", &SlowPile::add_car)
            .def("calculate_needed", &SlowPile::calculate_needed)
            .def("car_step", &SlowPile::car_step)
            .def("remove_car", &SlowPile::remove_car)
                    //////////////////////////////////////////////// inherit ChargePositionBase start
            .def_readwrite("position", &SlowPile::position)
            .def_readwrite("arrive_soc", &SlowPile::arrive_soc)
            .def_readwrite("target_soc", &SlowPile::target_soc)
            .def_readwrite("current_soc", &SlowPile::current_soc)
            .def_readwrite("current_power", &SlowPile::current_power)
            .def_readwrite("must_charge", &SlowPile::must_charge)
            .def_readwrite("emergency", &SlowPile::emergency)
            .def_readwrite("stay_time", &SlowPile::stay_time)
            .def_readwrite("already_stay_time", &SlowPile::already_stay_time)

            .def("pl_reset", &SlowPile::pl_reset)
            .def("reset_position", &SlowPile::reset_position)
            .def("occupy_charge", &SlowPile::occupy_charge)
        //////////////////////////////////////////////// inherit ChargePositionBase end
            ;

    class_<FastPile>("FastPile", init<int, Station *>())
            .def("add_car", &FastPile::add_car)
            .def("calculate_needed", &FastPile::calculate_needed)
            .def("car_step", &FastPile::car_step)
            .def("remove_car", &FastPile::remove_car)
                    //////////////////////////////////////////////// inherit ChargePositionBase start
            .def_readwrite("position", &FastPile::position)
            .def_readwrite("arrive_soc", &FastPile::arrive_soc)
            .def_readwrite("target_soc", &FastPile::target_soc)
            .def_readwrite("current_soc", &FastPile::current_soc)
            .def_readwrite("current_power", &FastPile::current_power)
            .def_readwrite("must_charge", &FastPile::must_charge)
            .def_readwrite("emergency", &FastPile::emergency)
            .def_readwrite("stay_time", &FastPile::stay_time)
            .def_readwrite("already_stay_time", &FastPile::already_stay_time)

            .def("pl_reset", &FastPile::pl_reset)
            .def("reset_position", &FastPile::reset_position)
            .def("occupy_charge", &FastPile::occupy_charge);
    //////////////////////////////////////////////// inherit ChargePositionBase end
    ;

    class_<SlowChargeStation>("SlowChargeStation", init<int>())
            .def(init<int, bool>())
            .def(init<int, bool, bool>())
            .def(init<int, bool, bool, std::string>())
            .def_readwrite("charge_power_upper_limit", &SlowChargeStation::charge_power_upper_limit)
            .def_readwrite("constant_power", &SlowChargeStation::constant_power)
            .def_readwrite("transformer_limit", &SlowChargeStation::transformer_limit)
            .def_readwrite("positions", &SlowChargeStation::positions)

                    //////////////////////////// wrapper start
            .def("evs_step", &SlowChargeStation::evs_step_wrapper1)
            .def("evs_step", &SlowChargeStation::evs_step_wrapper2)
            .def("evs_step", &SlowChargeStation::evs_step_wrapper3)
                    //////////////////////////// wrapper end
            .def("evs_reset", &SlowChargeStation::evs_reset)
            .def("calculate_output", &SlowChargeStation::calculate_output)
                    //////////////////////////////////////////////// inherit StationBase start
            .def("catch_load", &SlowChargeStation::catch_load_wrapper1)
            .def("catch_load", &SlowChargeStation::catch_load_wrapper2)

            .def("calculate_output", &SlowChargeStation::calculate_output)
            .def("print_situation", &SlowChargeStation::print_situation)
            .def("tell_empty", &SlowChargeStation::tell_empty)
            .def("tell_chargeable", &SlowChargeStation::tell_chargeable)
            .def("assign_car", &SlowChargeStation::assign_car)
                    //////////////////////////////////////////////// inherit StationBase end

                    //////////////////////////////////////////////// inherit Station start
            .def_readwrite("charge_number", &SlowChargeStation::charge_number)
            .def_readwrite("situation", &SlowChargeStation::situation)
            .def_readwrite("station_time_hole", &SlowChargeStation::station_time_hole)
            .def_readwrite("load_assigned", &SlowChargeStation::load_assigned)
            .def_readwrite("flow_in_number", &SlowChargeStation::flow_in_number)
            .def_readwrite("no_charge_list", &SlowChargeStation::no_charge_list)
            .def_readwrite("no_charge_number", &SlowChargeStation::no_charge_number)
            .def_readwrite("empty_list", &SlowChargeStation::empty_list)
            .def_readwrite("empty_number", &SlowChargeStation::empty_number)
            .def_readwrite("min_power", &SlowChargeStation::min_power)
            .def_readwrite("max_power", &SlowChargeStation::max_power)
            .def_readwrite("charge_power", &SlowChargeStation::charge_power)
            .def_readwrite("car_number", &SlowChargeStation::car_number)
            .def_readwrite("show", &SlowChargeStation::show)
            .def_readwrite("wait", &SlowChargeStation::wait)
            .def_readwrite("line", &SlowChargeStation::line)
            .def_readwrite("constant_charging", &SlowChargeStation::constant_charging)
            .def_readwrite("max_line", &SlowChargeStation::max_line)

            .def("print_situation", &SlowChargeStation::print_situation)
//            .def_pickle(SlowChargeStation_picklers())
        //////////////////////////////////////////////// inherit Station end
            ;

    class_<FastChargeStation>("FastChargeStation", init<int>())
            .def(init<int, bool>())
            .def(init<int, bool, bool>())
            .def(init<int, bool, bool, std::string>())
            .def_readwrite("charge_power_upper_limit", &FastChargeStation::charge_power_upper_limit)
            .def_readwrite("constant_power", &FastChargeStation::constant_power)
            .def_readwrite("transformer_limit", &FastChargeStation::transformer_limit)
            .def_readwrite("positions", &FastChargeStation::positions)

                    //////////////////////////// wrapper start
            .def("evs_step", &FastChargeStation::evs_step_wrapper1)
            .def("evs_step", &FastChargeStation::evs_step_wrapper2)
            .def("evs_step", &FastChargeStation::evs_step_wrapper3)
                    //////////////////////////// wrapper end
            .def("evs_reset", &FastChargeStation::evs_reset)
            .def("calculate_output", &FastChargeStation::calculate_output)

                    //////////////////////////////////////////////// inherit StationBase start
            .def("catch_load", &FastChargeStation::catch_load_wrapper1)
            .def("catch_load", &FastChargeStation::catch_load_wrapper2)

            .def("calculate_output", &FastChargeStation::calculate_output)
            .def("print_situation", &FastChargeStation::print_situation)
            .def("tell_empty", &FastChargeStation::tell_empty)
            .def("tell_chargeable", &FastChargeStation::tell_chargeable)
            .def("assign_car", &FastChargeStation::assign_car)
                    //////////////////////////////////////////////// inherit StationBase end

                    //////////////////////////////////////////////// inherit Station start
            .def_readwrite("charge_number", &FastChargeStation::charge_number)
            .def_readwrite("situation", &FastChargeStation::situation)
            .def_readwrite("station_time_hole", &FastChargeStation::station_time_hole)
            .def_readwrite("load_assigned", &FastChargeStation::load_assigned)
            .def_readwrite("flow_in_number", &FastChargeStation::flow_in_number)
            .def_readwrite("no_charge_list", &FastChargeStation::no_charge_list)
            .def_readwrite("no_charge_number", &FastChargeStation::no_charge_number)
            .def_readwrite("empty_list", &FastChargeStation::empty_list)
            .def_readwrite("empty_number", &FastChargeStation::empty_number)
            .def_readwrite("min_power", &FastChargeStation::min_power)
            .def_readwrite("max_power", &FastChargeStation::max_power)
            .def_readwrite("charge_power", &FastChargeStation::charge_power)
            .def_readwrite("car_number", &FastChargeStation::car_number)
            .def_readwrite("show", &FastChargeStation::show)
            .def_readwrite("wait", &FastChargeStation::wait)
            .def_readwrite("line", &FastChargeStation::line)
            .def_readwrite("constant_charging", &FastChargeStation::constant_charging)
            .def_readwrite("max_line", &FastChargeStation::max_line)

            .def("print_situation", &FastChargeStation::print_situation)

        //////////////////////////////////////////////// inherit Station end
            ;



//    class_<>()
//            .def("", &);


}



//int main() {
//
//    testSCP();
////    int k=-3;
////    int n=7;
////    int a=((-8%n)+n)%n;
////
////    cout<<a<<endl;
//    return 0;
//}


