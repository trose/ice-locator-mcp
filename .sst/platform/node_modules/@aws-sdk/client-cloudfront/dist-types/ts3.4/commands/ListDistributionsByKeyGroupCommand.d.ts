import { EndpointParameterInstructions } from "@smithy/middleware-endpoint";
import { Command as $Command } from "@smithy/smithy-client";
import {
  Handler,
  HttpHandlerOptions as __HttpHandlerOptions,
  MetadataBearer as __MetadataBearer,
  MiddlewareStack,
} from "@smithy/types";
import {
  CloudFrontClientResolvedConfig,
  ServiceInputTypes,
  ServiceOutputTypes,
} from "../CloudFrontClient";
import {
  ListDistributionsByKeyGroupRequest,
  ListDistributionsByKeyGroupResult,
} from "../models/models_1";
export { __MetadataBearer, $Command };
export interface ListDistributionsByKeyGroupCommandInput
  extends ListDistributionsByKeyGroupRequest {}
export interface ListDistributionsByKeyGroupCommandOutput
  extends ListDistributionsByKeyGroupResult,
    __MetadataBearer {}
export declare class ListDistributionsByKeyGroupCommand extends $Command<
  ListDistributionsByKeyGroupCommandInput,
  ListDistributionsByKeyGroupCommandOutput,
  CloudFrontClientResolvedConfig
> {
  readonly input: ListDistributionsByKeyGroupCommandInput;
  static getEndpointParameterInstructions(): EndpointParameterInstructions;
  constructor(input: ListDistributionsByKeyGroupCommandInput);
  resolveMiddleware(
    clientStack: MiddlewareStack<ServiceInputTypes, ServiceOutputTypes>,
    configuration: CloudFrontClientResolvedConfig,
    options?: __HttpHandlerOptions
  ): Handler<
    ListDistributionsByKeyGroupCommandInput,
    ListDistributionsByKeyGroupCommandOutput
  >;
  private serialize;
  private deserialize;
}
